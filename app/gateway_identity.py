from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def local_app_data() -> Path:
    configured = os.environ.get("LOCALAPPDATA")
    if configured:
        return Path(configured)
    return Path.home() / "AppData" / "Local"


IDENTITY_DIR = local_app_data() / "OpenClawWebUI" / "identity"
IDENTITY_FILE = IDENTITY_DIR / "device.json"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


@dataclass(frozen=True)
class DeviceIdentity:
    device_id: str
    public_key: str
    private_key: Ed25519PrivateKey

    def sign_base64url(self, payload: str) -> str:
        return _b64url(self.private_key.sign(payload.encode("utf-8")))


def generate_identity() -> DeviceIdentity:
    private_key = Ed25519PrivateKey.generate()
    public_key_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return DeviceIdentity(
        device_id=hashlib.sha256(public_key_bytes).hexdigest(),
        public_key=_b64url(public_key_bytes),
        private_key=private_key,
    )


def save_identity(
    identity: DeviceIdentity,
    identity_file: Path | None = None,
) -> None:
    destination = identity_file or IDENTITY_FILE
    destination.parent.mkdir(parents=True, exist_ok=True)
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
    temporary_file = destination.with_suffix(destination.suffix + ".tmp")
    temporary_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.chmod(temporary_file, 0o600)
    temporary_file.replace(destination)


def load_identity(identity_file: Path | None = None) -> DeviceIdentity:
    source = identity_file or IDENTITY_FILE
    data = json.loads(source.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise ValueError("Unsupported stored device identity version")
    private_key = serialization.load_pem_private_key(
        data["privateKeyPem"].encode("utf-8"),
        password=None,
    )
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Stored private key is not Ed25519")
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    expected_device_id = hashlib.sha256(public_key_bytes).hexdigest()
    if expected_device_id != data.get("deviceId"):
        raise ValueError("Stored device identity failed validation")
    expected_public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    if expected_public_key_pem != data.get("publicKeyPem"):
        raise ValueError("Stored public key failed validation")
    return DeviceIdentity(
        device_id=expected_device_id,
        public_key=_b64url(public_key_bytes),
        private_key=private_key,
    )


def load_or_create_identity(identity_file: Path | None = None) -> DeviceIdentity:
    destination = identity_file or IDENTITY_FILE
    if destination.exists():
        return load_identity(destination)
    identity = generate_identity()
    save_identity(identity, destination)
    return identity
