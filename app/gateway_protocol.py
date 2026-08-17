from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.gateway_config import GatewaySettings
from app.gateway_identity import DeviceIdentity


MAX_PREAUTH_PAYLOAD_BYTES = 64 * 1024
REQUIRED_METHODS = {
    "chat.history",
    "chat.send",
    "sessions.list",
    "chat.abort",
    "agent.wait",
}


class GatewayProtocolError(RuntimeError):
    pass


@dataclass(frozen=True)
class ConnectChallenge:
    nonce: str
    timestamp_ms: int


def encode_frame(frame: dict[str, Any]) -> str:
    return json.dumps(frame, separators=(",", ":"), ensure_ascii=False)


def decode_frame(raw_frame: str, max_bytes: int | None = None) -> dict[str, Any]:
    if max_bytes is not None and len(raw_frame.encode("utf-8")) > max_bytes:
        raise GatewayProtocolError("Gateway frame exceeds the allowed size")
    try:
        frame = json.loads(raw_frame)
    except json.JSONDecodeError as error:
        raise GatewayProtocolError("Gateway sent invalid JSON") from error
    if not isinstance(frame, dict):
        raise GatewayProtocolError("Gateway frame must be a JSON object")
    frame_type = frame.get("type")
    if frame_type not in {"req", "res", "event"}:
        raise GatewayProtocolError("Gateway frame has an unknown type")
    return frame


def parse_connect_challenge(frame: dict[str, Any]) -> ConnectChallenge:
    if frame.get("type") != "event" or frame.get("event") != "connect.challenge":
        raise GatewayProtocolError("Expected connect.challenge as the first frame")
    payload = frame.get("payload")
    if not isinstance(payload, dict):
        raise GatewayProtocolError("Connect challenge payload is invalid")
    nonce = payload.get("nonce")
    timestamp_ms = payload.get("ts")
    if not isinstance(nonce, str) or not nonce.strip():
        raise GatewayProtocolError("Connect challenge nonce is missing")
    if not isinstance(timestamp_ms, int) or timestamp_ms < 0:
        raise GatewayProtocolError("Connect challenge timestamp is invalid")
    return ConnectChallenge(nonce=nonce, timestamp_ms=timestamp_ms)


def build_device_auth_payload_v3(
    *,
    device_id: str,
    client_id: str,
    client_mode: str,
    role: str,
    scopes: tuple[str, ...],
    signed_at_ms: int,
    token: str | None,
    nonce: str,
    platform: str,
    device_family: str,
) -> str:
    normalized_platform = platform.strip().lower()
    normalized_device_family = device_family.strip().lower()
    return "|".join(
        (
            "v3",
            device_id,
            client_id,
            client_mode,
            role,
            ",".join(scopes),
            str(signed_at_ms),
            token or "",
            nonce,
            normalized_platform,
            normalized_device_family,
        )
    )


def build_connect_request(
    *,
    settings: GatewaySettings,
    identity: DeviceIdentity,
    nonce: str,
    auth_token: str | None,
    request_id: str | None = None,
    signed_at_ms: int | None = None,
) -> dict[str, Any]:
    settings.validate()
    actual_request_id = request_id or str(uuid4())
    actual_signed_at_ms = signed_at_ms or int(time.time() * 1000)
    signature_payload = build_device_auth_payload_v3(
        device_id=identity.device_id,
        client_id=settings.client_id,
        client_mode=settings.client_mode,
        role=settings.role,
        scopes=settings.scopes,
        signed_at_ms=actual_signed_at_ms,
        token=auth_token,
        nonce=nonce,
        platform=settings.platform,
        device_family=settings.device_family,
    )
    params: dict[str, Any] = {
        "minProtocol": settings.min_protocol,
        "maxProtocol": settings.max_protocol,
        "client": {
            "id": settings.client_id,
            "version": settings.client_version,
            "platform": settings.platform,
            "deviceFamily": settings.device_family,
            "mode": settings.client_mode,
        },
        "role": settings.role,
        "scopes": list(settings.scopes),
        "caps": [],
        "commands": [],
        "permissions": {},
        "locale": "en-US",
        "userAgent": f"openclaw-webui/{settings.client_version}",
        "device": {
            "id": identity.device_id,
            "publicKey": identity.public_key,
            "signature": identity.sign_base64url(signature_payload),
            "signedAt": actual_signed_at_ms,
            "nonce": nonce,
        },
    }
    if auth_token:
        params["auth"] = {"token": auth_token}
    return {
        "type": "req",
        "id": actual_request_id,
        "method": "connect",
        "params": params,
    }


def validate_hello_ok(
    response: dict[str, Any],
    *,
    request_id: str,
    settings: GatewaySettings,
) -> dict[str, Any]:
    if response.get("type") != "res" or response.get("id") != request_id:
        raise GatewayProtocolError("Connect response does not match the request")
    if response.get("ok") is not True:
        error = response.get("error")
        message = error.get("message") if isinstance(error, dict) else None
        raise GatewayProtocolError(message or "Gateway rejected the connection")
    payload = response.get("payload")
    if not isinstance(payload, dict) or payload.get("type") != "hello-ok":
        raise GatewayProtocolError("Gateway did not return hello-ok")
    if payload.get("protocol") != settings.max_protocol:
        raise GatewayProtocolError("Gateway negotiated an unexpected protocol version")
    auth = payload.get("auth")
    if not isinstance(auth, dict) or auth.get("role") != settings.role:
        raise GatewayProtocolError("Gateway returned an unexpected role")
    returned_scopes = auth.get("scopes")
    if not isinstance(returned_scopes, list) or not set(settings.scopes).issubset(
        returned_scopes
    ):
        raise GatewayProtocolError("Gateway did not grant the required scopes")
    features = payload.get("features")
    methods = features.get("methods") if isinstance(features, dict) else None
    if not isinstance(methods, list):
        raise GatewayProtocolError("Gateway did not advertise its method list")
    missing_methods = REQUIRED_METHODS.difference(methods)
    if missing_methods:
        missing = ", ".join(sorted(missing_methods))
        raise GatewayProtocolError(f"Gateway is missing required methods: {missing}")
    return payload


def build_request(
    method: str,
    params: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    if not method.strip():
        raise ValueError("Gateway method must not be blank")
    return {
        "type": "req",
        "id": request_id or str(uuid4()),
        "method": method,
        "params": params or {},
    }
