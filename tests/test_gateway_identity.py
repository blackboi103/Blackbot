from app.gateway_identity import (
    generate_identity,
    save_identity,
    load_identity,
)


def test_identity_round_trip(tmp_path, monkeypatch):
    import app.gateway_identity as identity_module

    identity_module.IDENTITY_DIR = tmp_path
    identity_module.IDENTITY_FILE = tmp_path / "device.json"

    original = generate_identity()

    save_identity(original)

    loaded = load_identity()

    assert loaded.device_id == original.device_id
    assert loaded.public_key == original.public_key

    message = b"identity-test"

    signature = loaded.private_key.sign(message)

    loaded.private_key.public_key().verify(
        signature,
        message,
    )


def test_identity_rejects_tampered_public_key(tmp_path):
    import json

    identity_file = tmp_path / "device.json"
    identity = generate_identity()
    save_identity(identity, identity_file)
    data = json.loads(identity_file.read_text(encoding="utf-8"))
    data["publicKeyPem"] = "tampered"
    identity_file.write_text(json.dumps(data), encoding="utf-8")

    import pytest

    with pytest.raises(ValueError, match="public key"):
        load_identity(identity_file)
