from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from app.gateway_identity import local_app_data


CREDENTIAL_DIR = local_app_data() / "OpenClawWebUI" / "credentials"
DEVICE_TOKEN_FILE = CREDENTIAL_DIR / "device-token.json"


@dataclass(frozen=True)
class DeviceToken:
    token: str
    role: str
    scopes: tuple[str, ...]


class DeviceTokenStore:
    def __init__(self, token_file: Path | None = None) -> None:
        self.token_file = token_file or DEVICE_TOKEN_FILE

    def load(self) -> DeviceToken | None:
        if not self.token_file.exists():
            return None
        data = json.loads(self.token_file.read_text(encoding="utf-8"))
        if data.get("version") != 1:
            raise ValueError("Unsupported stored device token version")
        token = data.get("token")
        role = data.get("role")
        scopes = data.get("scopes")
        if not isinstance(token, str) or not token:
            raise ValueError("Stored device token is invalid")
        if not isinstance(role, str) or not role:
            raise ValueError("Stored device token role is invalid")
        if not isinstance(scopes, list) or not all(
            isinstance(scope, str) for scope in scopes
        ):
            raise ValueError("Stored device token scopes are invalid")
        return DeviceToken(token=token, role=role, scopes=tuple(scopes))

    def save(self, device_token: DeviceToken) -> None:
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": 1,
            "token": device_token.token,
            "role": device_token.role,
            "scopes": list(device_token.scopes),
        }
        temporary_file = self.token_file.with_suffix(self.token_file.suffix + ".tmp")
        temporary_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.chmod(temporary_file, 0o600)
        temporary_file.replace(self.token_file)

    def clear(self) -> None:
        if self.token_file.exists():
            self.token_file.unlink()
