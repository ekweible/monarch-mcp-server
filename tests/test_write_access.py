"""Tests for default read-only write guard."""

import pytest

from monarch_mcp_server.tools.accounts import (
    refresh_accounts,
    upload_account_balance_history,
)
from monarch_mcp_server.tools.budgets import set_budget_amount
from monarch_mcp_server.tools.categories import (
    create_transaction_category,
    update_category,
)
from monarch_mcp_server.tools.merchants import review_recurring_stream, update_merchant
from monarch_mcp_server.tools.rules import (
    create_transaction_rule,
    delete_transaction_rule,
    update_transaction_rule,
)
from monarch_mcp_server.tools.splits import split_transaction
from monarch_mcp_server.tools.tags import (
    add_transaction_tag,
    create_transaction_tag,
    set_transaction_tags,
)
from monarch_mcp_server.tools.transactions import (
    bulk_categorize_transactions,
    categorize_transaction,
    create_transaction,
    delete_transaction,
    mark_transaction_reviewed,
    update_transaction,
    update_transaction_notes,
)


@pytest.mark.parametrize(
    ("tool", "args", "kwargs"),
    [
        (refresh_accounts, (), {}),
        (upload_account_balance_history, ("acc-1", '{"2026-01-01": 1}'), {}),
        (set_budget_amount, (100.0,), {"category_id": "cat-1"}),
        (create_transaction_category, ("grp-1", "Coffee"), {}),
        (update_category, ("cat-1",), {"name": "Coffee"}),
        (update_merchant, ("merchant-1",), {"name": "New Name"}),
        (review_recurring_stream, ("stream-1", "approved"), {}),
        (create_transaction_rule, (), {"merchant_criteria_value": "coffee"}),
        (update_transaction_rule, ("rule-1",), {"set_merchant_name": "Coffee"}),
        (delete_transaction_rule, ("rule-1",), {}),
        (split_transaction, ("txn-1", []), {}),
        (set_transaction_tags, ("txn-1", ["tag-1"]), {}),
        (add_transaction_tag, ("txn-1", "tag-1"), {}),
        (create_transaction_tag, ("new", "#000000"), {}),
        (
            create_transaction,
            (),
            {
                "date": "2026-01-01",
                "account_id": "acc-1",
                "amount": -1.0,
                "merchant_name": "Coffee",
                "category_id": "cat-1",
            },
        ),
        (update_transaction, ("txn-1",), {"category_id": "cat-1"}),
        (categorize_transaction, ("txn-1", "cat-1"), {}),
        (update_transaction_notes, ("txn-1", "note"), {}),
        (mark_transaction_reviewed, ("txn-1",), {}),
        (bulk_categorize_transactions, (["txn-1"], "cat-1"), {}),
        (delete_transaction, ("txn-1",), {}),
    ],
)
async def test_mutating_tools_disabled_by_default(
    tool, args, kwargs, mock_monarch_client
):
    result = await tool(*args, **kwargs)

    assert "Write access disabled" in result
    assert not mock_monarch_client.method_calls
