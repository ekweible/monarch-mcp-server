"""Cached MonarchMoney client factory."""

import logging
from typing import Optional

from monarchmoney import MonarchMoney
from monarchmoney.monarchmoney import MonarchMoneyEndpoints

from monarch_mcp_server.secure_session import secure_session

logger = logging.getLogger(__name__)

# Patch MonarchMoney to use new API domain
MonarchMoneyEndpoints.BASE_URL = "https://api.monarch.com"

# Module-level client cache
_cached_client: Optional[MonarchMoney] = None


def clear_client_cache() -> None:
    """Clear the cached client. Call after re-authentication."""
    global _cached_client
    _cached_client = None
    logger.info("Client cache cleared")


async def get_monarch_client() -> MonarchMoney:
    """Get or create a cached MonarchMoney client using secure session storage."""
    global _cached_client

    if _cached_client is not None:
        return _cached_client

    # Try to get authenticated client from secure session
    client = secure_session.get_authenticated_client()

    if client is not None:
        logger.info("Using authenticated client from secure keyring storage")
        _cached_client = client
        return client

    raise RuntimeError("Authentication needed! Run: python login_setup.py")
