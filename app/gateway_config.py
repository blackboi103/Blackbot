from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from urllib.parse import urlparse


GATEWAY_TOKEN_ENV = "OPENCLAW_GATEWAY_TOKEN"


@dataclass(frozen=True)
class GatewaySettings:
    url: str = "ws://127.0.0.1:18789"
    shared_token: str | None = None
    min_protocol: int = 4
    max_protocol: int = 4
    client_id: str = "cli"
    client_mode: str = "cli"
    client_version: str = "0.1.0"
    role: str = "operator"
    scopes: tuple[str, ...] = ("operator.read", "operator.write")
    platform: str = sys.platform
    device_family: str = "desktop"
    handshake_timeout_seconds: float = 15.0
    request_timeout_seconds: float = 30.0
    allow_remote_gateway: bool = False

    @classmethod
    def from_environment(cls) -> GatewaySettings:
        settings = cls(
            url=os.environ.get("OPENCLAW_GATEWAY_URL", cls.url),
            shared_token=os.environ.get(GATEWAY_TOKEN_ENV),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        parsed = urlparse(self.url)
        if parsed.scheme not in {"ws", "wss"}:
            raise ValueError("Gateway URL must use ws:// or wss://")
        if not parsed.hostname:
            raise ValueError("Gateway URL must include a hostname")
        loopback_hosts = {"127.0.0.1", "localhost", "::1"}
        if not self.allow_remote_gateway and parsed.hostname not in loopback_hosts:
            raise ValueError("Remote Gateway connections are disabled")
        if self.min_protocol != 4 or self.max_protocol != 4:
            raise ValueError("This prototype requires OpenClaw protocol 4")
        if self.role != "operator":
            raise ValueError("This prototype supports only the operator role")
        if self.scopes != ("operator.read", "operator.write"):
            raise ValueError(
                "This prototype requires exactly operator.read and operator.write"
            )
