import pytest

from app.gateway_config import GATEWAY_TOKEN_ENV, GatewaySettings


def test_gateway_settings_load_loopback_environment(monkeypatch):
    monkeypatch.setenv("OPENCLAW_GATEWAY_URL", "ws://localhost:18789")
    monkeypatch.setenv(GATEWAY_TOKEN_ENV, "test-token")

    settings = GatewaySettings.from_environment()

    assert settings.url == "ws://localhost:18789"
    assert settings.shared_token == "test-token"
    assert settings.scopes == ("operator.read", "operator.write")


def test_gateway_settings_reject_remote_host_by_default(monkeypatch):
    monkeypatch.setenv("OPENCLAW_GATEWAY_URL", "ws://192.168.1.25:18789")

    with pytest.raises(ValueError, match="Remote Gateway connections are disabled"):
        GatewaySettings.from_environment()


def test_gateway_settings_reject_scope_expansion():
    settings = GatewaySettings(
        scopes=("operator.read", "operator.write", "operator.admin")
    )

    with pytest.raises(ValueError, match="exactly operator.read"):
        settings.validate()
