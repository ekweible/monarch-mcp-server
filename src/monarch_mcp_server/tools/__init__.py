"""Tool modules – importing this package registers all tools with the FastMCP instance."""

from monarch_mcp_server.tools import (  # noqa: F401
    accounts,
    auth,
    budgets,
    categories,
    financial,
    merchants,
    rules,
    splits,
    summaries,
    tags,
    transactions,
)
