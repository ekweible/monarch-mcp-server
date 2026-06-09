"""Authentication tools."""

import logging

from monarch_mcp_server.app import mcp
from monarch_mcp_server.secure_session import secure_session

logger = logging.getLogger(__name__)


@mcp.tool()
async def setup_authentication() -> str:
    """Get instructions for setting up secure authentication with Monarch Money."""
    return """🔐 Monarch Money - One-Time Setup

Authentication is terminal-only in this fork.

1️⃣ Open Terminal and run:
   python login_setup.py

Call 'monarch_logout' to clear the stored session.

✅ Session persists across restarts
✅ Token stored securely in system keyring
✅ Write tools stay disabled unless MONARCH_ENABLE_WRITES=true"""


async def monarch_login() -> str:
    """Internal compatibility stub; not registered as an MCP tool."""
    return "MCP login is disabled in this fork. Run: python login_setup.py"


async def monarch_login_with_token() -> str:
    """Internal compatibility stub; not registered as an MCP tool."""
    return "MCP token login is disabled in this fork. Run: python login_setup.py"


@mcp.tool()
async def monarch_logout() -> str:
    """Clear the stored Monarch Money session from the system keyring."""
    secure_session.delete_token()
    return "Cleared stored Monarch session."


@mcp.tool()
async def check_auth_status() -> str:
    """Check if already authenticated with Monarch Money."""
    try:
        token = secure_session.load_token()
        if token:
            status = "✅ Authentication appears configured. Try get_accounts to verify access."
        else:
            status = "🔐 Authentication required. Run: python login_setup.py"
        return status
    except Exception:
        return "Authentication status unavailable. Run python login_setup.py if needed."


async def debug_session_loading() -> str:
    """Internal compatibility stub; not registered as an MCP tool."""
    return "Authentication debugging is disabled in this fork."
