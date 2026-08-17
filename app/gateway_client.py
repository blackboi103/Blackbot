from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Any, Awaitable, Callable
from uuid import uuid4

from websockets.asyncio.client import connect as websocket_connect

from app.gateway_config import GatewaySettings
from app.gateway_credentials import DeviceToken, DeviceTokenStore
from app.gateway_identity import DeviceIdentity
from app.gateway_protocol import (
    MAX_PREAUTH_PAYLOAD_BYTES,
    GatewayProtocolError,
    build_connect_request,
    build_request,
    decode_frame,
    encode_frame,
    parse_connect_challenge,
    validate_hello_ok,
)


ConnectFactory = Callable[..., Awaitable[Any]]


class GatewayClientError(RuntimeError):
    pass


class GatewayRequestError(GatewayClientError):
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        retryable: bool = False,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.details = details or {}

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> GatewayRequestError:
        error = response.get("error")
        if not isinstance(error, dict):
            return cls("Gateway request failed")
        details = error.get("details")
        return cls(
            str(error.get("message") or "Gateway request failed"),
            code=error.get("code") if isinstance(error.get("code"), str) else None,
            retryable=error.get("retryable") is True,
            details=details if isinstance(details, dict) else None,
        )


class GatewayClient:
    def __init__(
        self,
        *,
        settings: GatewaySettings,
        identity: DeviceIdentity,
        token_store: DeviceTokenStore | None = None,
        connect_factory: ConnectFactory = websocket_connect,
    ) -> None:
        settings.validate()
        self.settings = settings
        self.identity = identity
        self.token_store = token_store or DeviceTokenStore()
        self.connect_factory = connect_factory
        self.hello: dict[str, Any] | None = None
        self._websocket: Any | None = None
        self._receiver_task: asyncio.Task[None] | None = None
        self._pending: dict[str, asyncio.Future[Any]] = {}
        self._events: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=500)
        self._max_payload_bytes = 25 * 1024 * 1024

    @property
    def connected(self) -> bool:
        return self._websocket is not None and self.hello is not None

    async def __aenter__(self) -> GatewayClient:
        await self.connect()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def connect(self) -> dict[str, Any]:
        if self.connected:
            raise GatewayClientError("Gateway client is already connected")
        auth_token = self._select_auth_token()
        try:
            self._websocket = await self.connect_factory(
                self.settings.url,
                open_timeout=self.settings.handshake_timeout_seconds,
                max_size=self._max_payload_bytes,
            )
            challenge_raw = await asyncio.wait_for(
                self._websocket.recv(),
                timeout=self.settings.handshake_timeout_seconds,
            )
            challenge_frame = decode_frame(
                self._require_text_frame(challenge_raw),
                max_bytes=MAX_PREAUTH_PAYLOAD_BYTES,
            )
            challenge = parse_connect_challenge(challenge_frame)
            connect_request = build_connect_request(
                settings=self.settings,
                identity=self.identity,
                nonce=challenge.nonce,
                auth_token=auth_token,
            )
            await self._websocket.send(encode_frame(connect_request))
            response_raw = await asyncio.wait_for(
                self._websocket.recv(),
                timeout=self.settings.handshake_timeout_seconds,
            )
            response = decode_frame(
                self._require_text_frame(response_raw),
                max_bytes=MAX_PREAUTH_PAYLOAD_BYTES,
            )
            if response.get("ok") is not True:
                raise GatewayRequestError.from_response(response)
            self.hello = validate_hello_ok(
                response,
                request_id=connect_request["id"],
                settings=self.settings,
            )
            policy = self.hello.get("policy")
            if isinstance(policy, dict):
                max_payload = policy.get("maxPayload")
                if isinstance(max_payload, int) and max_payload > 0:
                    self._max_payload_bytes = max_payload
            self._persist_issued_device_token(self.hello)
            self._receiver_task = asyncio.create_task(self._receive_loop())
            return self.hello
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        receiver_task = self._receiver_task
        self._receiver_task = None
        if receiver_task is not None:
            receiver_task.cancel()
            with suppress(asyncio.CancelledError):
                await receiver_task
        websocket = self._websocket
        self._websocket = None
        self.hello = None
        if websocket is not None:
            with suppress(Exception):
                await websocket.close()
        self._fail_pending(GatewayClientError("Gateway connection closed"))

    async def request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        if not self.connected or self._websocket is None:
            raise GatewayClientError("Gateway client is not connected")
        request = build_request(method, params)
        request_id = request["id"]
        future = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future
        try:
            await self._websocket.send(encode_frame(request))
            return await asyncio.wait_for(
                future,
                timeout=self.settings.request_timeout_seconds,
            )
        except TimeoutError as error:
            raise GatewayClientError(f"Gateway request timed out: {method}") from error
        finally:
            self._pending.pop(request_id, None)

    async def next_event(self, timeout_seconds: float | None = None) -> dict[str, Any]:
        if timeout_seconds is None:
            return await self._events.get()
        return await asyncio.wait_for(self._events.get(), timeout=timeout_seconds)

    async def sessions_list(self, limit: int = 50) -> Any:
        if limit < 1:
            raise ValueError("Session limit must be positive")
        return await self.request("sessions.list", {"limit": limit})

    async def chat_history(
        self,
        session_key: str,
        *,
        limit: int = 100,
        max_chars: int = 100_000,
    ) -> Any:
        self._require_non_blank(session_key, "session_key")
        return await self.request(
            "chat.history",
            {
                "sessionKey": session_key,
                "limit": limit,
                "maxChars": max_chars,
            },
        )

    async def chat_send(
        self,
        session_key: str,
        message: str,
        *,
        session_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Any:
        self._require_non_blank(session_key, "session_key")
        self._require_non_blank(message, "message")
        params: dict[str, Any] = {
            "sessionKey": session_key,
            "message": message,
            "idempotencyKey": idempotency_key or str(uuid4()),
        }
        if session_id:
            params["sessionId"] = session_id
        return await self.request("chat.send", params)

    async def chat_abort(
        self,
        session_key: str,
        *,
        run_id: str | None = None,
    ) -> Any:
        self._require_non_blank(session_key, "session_key")
        params: dict[str, Any] = {"sessionKey": session_key}
        if run_id:
            params["runId"] = run_id
        return await self.request("chat.abort", params)

    async def agent_wait(
        self,
        run_id: str,
        *,
        timeout_ms: int | None = None,
    ) -> Any:
        self._require_non_blank(run_id, "run_id")
        params: dict[str, Any] = {"runId": run_id}
        if timeout_ms is not None:
            params["timeoutMs"] = timeout_ms
        return await self.request("agent.wait", params)

    async def _receive_loop(self) -> None:
        assert self._websocket is not None
        try:
            while True:
                raw_frame = await self._websocket.recv()
                frame = decode_frame(
                    self._require_text_frame(raw_frame),
                    max_bytes=self._max_payload_bytes,
                )
                if frame.get("type") == "res":
                    self._resolve_response(frame)
                elif frame.get("type") == "event":
                    self._queue_event(frame)
        except asyncio.CancelledError:
            raise
        except Exception:
            self._fail_pending(GatewayClientError("Gateway receive loop stopped"))
            self.hello = None
            websocket = self._websocket
            self._websocket = None
            if websocket is not None:
                with suppress(Exception):
                    await websocket.close()

    def _resolve_response(self, response: dict[str, Any]) -> None:
        request_id = response.get("id")
        if not isinstance(request_id, str):
            return
        future = self._pending.get(request_id)
        if future is None or future.done():
            return
        if response.get("ok") is True:
            future.set_result(response.get("payload"))
        else:
            future.set_exception(GatewayRequestError.from_response(response))

    def _queue_event(self, event: dict[str, Any]) -> None:
        if self._events.full():
            with suppress(asyncio.QueueEmpty):
                self._events.get_nowait()
        self._events.put_nowait(event)

    def _select_auth_token(self) -> str:
        stored_token = self.token_store.load()
        if (
            stored_token is not None
            and stored_token.role == self.settings.role
            and stored_token.scopes == self.settings.scopes
        ):
            return stored_token.token
        if self.settings.shared_token:
            return self.settings.shared_token
        raise GatewayClientError(
            "No Gateway token is available in the environment or device-token store"
        )

    def _persist_issued_device_token(self, hello: dict[str, Any]) -> None:
        auth = hello.get("auth")
        if not isinstance(auth, dict):
            return
        token = auth.get("deviceToken")
        role = auth.get("role")
        scopes = auth.get("scopes")
        if (
            isinstance(token, str)
            and token
            and isinstance(role, str)
            and isinstance(scopes, list)
            and all(isinstance(scope, str) for scope in scopes)
        ):
            self.token_store.save(
                DeviceToken(token=token, role=role, scopes=tuple(scopes))
            )

    def _fail_pending(self, error: Exception) -> None:
        for future in self._pending.values():
            if not future.done():
                future.set_exception(error)
        self._pending.clear()

    @staticmethod
    def _require_text_frame(raw_frame: Any) -> str:
        if not isinstance(raw_frame, str):
            raise GatewayProtocolError("Gateway must use WebSocket text frames")
        return raw_frame

    @staticmethod
    def _require_non_blank(value: str, field_name: str) -> None:
        if not value.strip():
            raise ValueError(f"{field_name} must not be blank")
