"""Tests for auth hardening policy."""

from monarch_mcp_server.tools import auth as tools_auth


class TestAuthPolicy:
    async def test_mcp_login_is_not_registered_tool(self):
        result = await tools_auth.monarch_login()
        assert "MCP login is disabled" in result
        assert "login_setup.py" in result

    async def test_mcp_token_login_is_not_registered_tool(self):
        result = await tools_auth.monarch_login_with_token()
        assert "MCP token login is disabled" in result
        assert "login_setup.py" in result

    async def test_debug_session_loading_is_not_registered_tool(self):
        result = await tools_auth.debug_session_loading()
        assert result == "Authentication debugging is disabled in this fork."
