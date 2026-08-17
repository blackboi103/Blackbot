from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


IDENTITY_DIR = (
    Path.home()
    / "AppData"
    / "Local"
    / "OpenClawWebUI"
    / "identity"
)

IDENTITY_FILE = IDENTITY_DIR / "device.json"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


@dataclass
class DeviceIdentity:
    device_id: str
    public_key: str
    private_key: Ed25519PrivateKey


def generate_identity() -> DeviceIdentity:
    private_key = Ed25519PrivateKey.generate()

    public_key_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    device_id = hashlib.sha256(public_key_bytes).hexdigest()

    public_key = _b64url(public_key_bytes)

    return DeviceIdentity(
        device_id=device_id,
        public_key=public_key,
        private_key=private_key,
    )


def save_identity(identity: DeviceIdentity) -> None:
    IDENTITY_DIR.mkdir(parents=True, exist_ok=True)

    private_key_pem = identity.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_key_pem = identity.private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    data = {
        "version": 1,
        "deviceId": identity.device_id,
        "publicKeyPem": public_key_pem,
        "privateKeyPem": private_key_pem,
    }

    temp_file = IDENTITY_FILE.with_suffix(".tmp")

    temp_file.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    temp_file.replace(IDENTITY_FILE)


def load_identity() -> DeviceIdentity:
    data = json.loads(
        IDENTITY_FILE.read_text(encoding="utf-8")
    )

    private_key = serialization.load_pem_private_key(
        data["privateKeyPem"].encode("utf-8"),
        password=None,
    )

    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Stored private key is not Ed25519")

    public_key_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    expected_device_id = hashlib.sha256(
        public_key_bytes
    ).hexdigest()

    if expected_device_id != data["deviceId"]:
        raise ValueError("Stored device identity failed validation")

    return DeviceIdentity(
        device_id=data["deviceId"],
        public_key=_b64url(public_key_bytes),
        private_key=private_key,
    )