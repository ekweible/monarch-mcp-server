"""Backward-compatibility shim for the modular tool layout."""

from monarch_mcp_server.app import app, main, mcp  # noqa: F401
from monarch_mcp_server.client import get_monarch_client  # noqa: F401
from monarch_mcp_server.tools.accounts import (  # noqa: F401
    get_account_balance_history,
    get_account_holdings,
    get_accounts,
    refresh_accounts,
    upload_account_balance_history,
)
from monarch_mcp_server.tools.auth import (  # noqa: F401
    check_auth_status,
    debug_session_loading,
    monarch_login,
    monarch_login_with_token,
    monarch_logout,
    setup_authentication,
)
from monarch_mcp_server.tools.budgets import (  # noqa: F401
    get_budgets,
    set_budget_amount,
)
from monarch_mcp_server.tools.categories import (  # noqa: F401
    create_transaction_category,
    get_cashflow_by_month,
    get_category_details,
    get_transaction_categories,
    get_transaction_category_groups,
    update_category,
)
from monarch_mcp_server.tools.financial import (  # noqa: F401
    get_cashflow,
    get_net_worth,
    get_net_worth_by_account_type,
)
from monarch_mcp_server.tools.merchants import (  # noqa: F401
    get_merchant,
    review_recurring_stream,
    update_merchant,
)
from monarch_mcp_server.tools.rules import (  # noqa: F401
    create_transaction_rule,
    delete_transaction_rule,
    get_transaction_rules,
    update_transaction_rule,
)
from monarch_mcp_server.tools.splits import (  # noqa: F401
    get_transaction_splits,
    split_transaction,
)
from monarch_mcp_server.tools.summaries import (  # noqa: F401
    get_spending_summary,
    get_transactions_summary,
)
from monarch_mcp_server.tools.tags import (  # noqa: F401
    add_transaction_tag,
    create_transaction_tag,
    get_transaction_tags,
    set_transaction_tags,
)
from monarch_mcp_server.tools.transactions import (  # noqa: F401
    bulk_categorize_transactions,
    categorize_transaction,
    create_transaction,
    delete_transaction,
    get_recurring_transactions,
    get_transaction_details,
    get_transactions,
    get_transactions_needing_review,
    mark_transaction_reviewed,
    search_transactions,
    update_transaction,
    update_transaction_notes,
)

if __name__ == "__main__":
    main()
