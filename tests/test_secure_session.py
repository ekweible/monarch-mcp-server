"""Tests for secure session helpers."""

import keyring

from monarch_mcp_server import secure_session


def test_keyring_available_accepts_macos_backend(monkeypatch):
    macos_backend_type = type("Keyring", (), {"__module__": "keyring.backends.macOS"})

    monkeypatch.setattr(keyring, "get_keyring", lambda: macos_backend_type())

    assert secure_session._keyring_available() is True


def test_keyring_available_rejects_fail_backend(monkeypatch):
    fail_backend_type = type("Keyring", (), {"__module__": "keyring.backends.fail"})

    monkeypatch.setattr(keyring, "get_keyring", lambda: fail_backend_type())

    assert secure_session._keyring_available() is False
