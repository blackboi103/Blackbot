from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_mission_control_replaces_the_old_chat_interface():
    html = (PROJECT_ROOT / "static" / "index.html").read_text(encoding="utf-8")

    assert 'id="kanban-board"' in html
    assert 'id="activity-list"' in html
    assert "Mission Control" in html
    assert 'id="chat-form"' not in html
    assert 'id="message-input"' not in html


def test_browser_assets_do_not_contain_gateway_credentials():
    browser_source = "\n".join(
        (PROJECT_ROOT / "static" / filename).read_text(encoding="utf-8")
        for filename in ("index.html", "app.js", "styles.css")
    )

    assert "OPENCLAW_GATEWAY_TOKEN" not in browser_source
    assert "privateKeyPem" not in browser_source
    assert "device-token.json" not in browser_source


def test_step_21_api_connection_has_not_started():
    javascript = (PROJECT_ROOT / "static" / "app.js").read_text(encoding="utf-8")

    assert "/api/tasks" not in javascript
    assert "/api/activity" not in javascript
