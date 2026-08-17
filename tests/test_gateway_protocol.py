import asyncio
import base64
import json

import pytest

from app.gateway_client import GatewayClient
from app.gateway_config import GatewaySettings
from app.gateway_credentials import DeviceToken, DeviceTokenStore
from app.gateway_identity import generate_identity
from app.gateway_protocol import (
    GatewayProtocolError,
    build_connect_request,
    build_device_auth_payload_v3,
    decode_frame,
    validate_hello_ok,
)


REQUIRED_METHODS = [
    "chat.history",
    "chat.send",
    "sessions.list",
    "chat.abort",
    "agent.wait",
]


def hello_response(request_id, device_token=None):
    auth = {
        "role": "operator",
        "scopes": ["operator.read", "operator.write"],
    }
    if device_token:
        auth["deviceToken"] = device_token
    return {
        "type": "res",
        "id": request_id,
        "ok": True,
        "payload": {
            "type": "hello-ok",
            "protocol": 4,
            "server": {"version": "test", "connId": "connection-1"},
            "features": {"methods": REQUIRED_METHODS, "events": ["chat", "tick"]},
            "snapshot": {},
            "auth": auth,
            "policy": {
                "maxPayload": 26214400,
                "maxBufferedBytes": 52428800,
                "tickIntervalMs": 15000,
            },
        },
    }


class FakeWebSocket:
    def __init__(self):
        self.incoming = asyncio.Queue()
        self.sent = []
        self.closed = False
        self.incoming.put_nowait(
            json.dumps(
                {
                    "type": "event",
                    "event": "connect.challenge",
                    "payload": {"nonce": "server-nonce", "ts": 1000},
                }
            )
        )

    async def send(self, raw_frame):
        frame = json.loads(raw_frame)
        self.sent.append(frame)
        if frame["method"] == "connect":
            self.incoming.put_nowait(json.dumps(hello_response(frame["id"], "device-token")))
        else:
            self.incoming.put_nowait(
                json.dumps(
                    {
                        "type": "event",
                        "event": "tick",
                        "payload": {"now": 123},
                    }
                )
            )
            self.incoming.put_nowait(
                json.dumps(
                    {
                        "type": "res",
                        "id": frame["id"],
                        "ok": True,
                        "payload": {"method": frame["method"]},
                    }
                )
            )

    async def recv(self):
        return await self.incoming.get()

    async def close(self):
        self.closed = True


def test_device_auth_payload_v3_matches_openclaw_field_order():
    payload = build_device_auth_payload_v3(
        device_id="device-id",
        client_id="cli",
        client_mode="cli",
        role="operator",
        scopes=("operator.read", "operator.write"),
        signed_at_ms=123456,
        token="secret-token",
        nonce="server-nonce",
        platform="Win32",
        device_family="Desktop",
    )

    assert payload == (
        "v3|device-id|cli|cli|operator|operator.read,operator.write|"
        "123456|secret-token|server-nonce|win32|desktop"
    )


def test_connect_request_signature_is_valid():
    identity = generate_identity()
    settings = GatewaySettings(shared_token="secret-token", platform="win32")
    request = build_connect_request(
        settings=settings,
        identity=identity,
        nonce="server-nonce",
        auth_token="secret-token",
        request_id="request-1",
        signed_at_ms=123456,
    )
    signature = request["params"]["device"]["signature"]
    padded_signature = signature + "=" * (-len(signature) % 4)
    payload = build_device_auth_payload_v3(
        device_id=identity.device_id,
        client_id="cli",
        client_mode="cli",
        role="operator",
        scopes=("operator.read", "operator.write"),
        signed_at_ms=123456,
        token="secret-token",
        nonce="server-nonce",
        platform="win32",
        device_family="desktop",
    )

    identity.private_key.public_key().verify(
        base64.urlsafe_b64decode(padded_signature),
        payload.encode("utf-8"),
    )
    assert request["params"]["auth"] == {"token": "secret-token"}
    assert request["params"]["minProtocol"] == 4


def test_hello_validation_fails_closed_on_missing_scope():
    settings = GatewaySettings(shared_token="secret-token")
    response = hello_response("request-1")
    response["payload"]["auth"]["scopes"] = ["operator.read"]

    with pytest.raises(GatewayProtocolError, match="required scopes"):
        validate_hello_ok(response, request_id="request-1", settings=settings)


def test_decode_frame_rejects_non_json():
    with pytest.raises(GatewayProtocolError, match="invalid JSON"):
        decode_frame("not-json")


def test_gateway_client_connects_and_correlates_requests(tmp_path):
    async def scenario():
        websocket = FakeWebSocket()

        async def fake_connect(*_args, **_kwargs):
            return websocket

        token_store = DeviceTokenStore(tmp_path / "device-token.json")
        client = GatewayClient(
            settings=GatewaySettings(shared_token="shared-token"),
            identity=generate_identity(),
            token_store=token_store,
            connect_factory=fake_connect,
        )
        hello = await client.connect()
        response = await client.sessions_list(limit=10)
        event = await client.next_event(timeout_seconds=1)
        stored_token = token_store.load()
        await client.close()

        assert hello["protocol"] == 4
        assert response == {"method": "sessions.list"}
        assert event["event"] == "tick"
        assert stored_token == DeviceToken(
            token="device-token",
            role="operator",
            scopes=("operator.read", "operator.write"),
        )
        assert websocket.closed is True

    asyncio.run(scenario())
