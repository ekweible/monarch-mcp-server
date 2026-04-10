"""Tests for Monarch MCP Server tools."""

import asyncio
import json

import pytest

import monarch_mcp_server.server as server_module
from monarch_mcp_server.server import (
    add_transaction_tag,
    categorize_transaction,
    check_auth_status,
    create_transaction,
    create_transaction_category,
    create_transaction_tag,
    get_account_holdings,
    get_accounts,
    get_budgets,
    get_cashflow,
    get_monarch_client,
    get_transaction_categories,
    get_transaction_category_groups,
    get_transaction_tags,
    get_transactions,
    refresh_accounts,
    set_transaction_tags,
    update_transaction,
)


class TestGetAccounts:
    def test_returns_formatted_account_list(self):
        result = json.loads(get_accounts())
        assert len(result) == 2
        assert result[0]["id"] == "acc-1"
        assert result[0]["name"] == "Checking Account"
        assert result[0]["type"] == "checking"
        assert result[0]["balance"] == 1500.00
        assert result[0]["institution"] == "Test Bank"
        assert result[0]["is_active"] is True
        assert result[0]["is_hidden"] is False

    def test_hidden_account_flagged(self):
        result = json.loads(get_accounts())
        assert result[1]["is_hidden"] is True

    def test_handles_null_type(self, mock_monarch_client):
        mock_monarch_client.get_accounts.return_value = {
            "accounts": [
                {
                    "id": "acc-3",
                    "displayName": "Unknown",
                    "type": None,
                    "currentBalance": 0,
                    "institution": None,
                    "deactivatedAt": None,
                    "isHidden": False,
                }
            ]
        }
        result = json.loads(get_accounts())
        assert result[0]["type"] is None
        assert result[0]["institution"] is None

    def test_handles_empty_accounts(self, mock_monarch_client):
        mock_monarch_client.get_accounts.return_value = {"accounts": []}
        result = json.loads(get_accounts())
        assert result == []

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.get_accounts.side_effect = Exception("API timeout")
        result = get_accounts()
        assert "Error getting accounts" in result
        assert "API timeout" in result


class TestGetTransactions:
    def test_returns_formatted_transactions(self):
        result = json.loads(get_transactions())
        assert len(result) == 2
        assert result[0]["id"] == "txn-1"
        assert result[0]["amount"] == -42.50
        assert result[0]["category"] == "Groceries"
        assert result[0]["merchant"] == "Whole Foods"

    def test_handles_null_merchant(self):
        result = json.loads(get_transactions())
        assert result[1]["merchant"] is None

    def test_handles_null_category(self, mock_monarch_client):
        mock_monarch_client.get_transactions.return_value = {
            "allTransactions": {
                "results": [
                    {
                        "id": "txn-3",
                        "date": "2026-03-03",
                        "amount": -10.00,
                        "description": "ATM",
                        "category": None,
                        "account": {"displayName": "Checking"},
                        "merchant": None,
                        "isPending": True,
                    }
                ]
            }
        }
        result = json.loads(get_transactions())
        assert result[0]["category"] is None
        assert result[0]["is_pending"] is True

    def test_passes_filters_to_client(self, mock_monarch_client):
        get_transactions(
            limit=10, offset=5, start_date="2026-03-01", account_id="acc-1"
        )
        mock_monarch_client.get_transactions.assert_called_once_with(
            limit=10,
            offset=5,
            start_date="2026-03-01",
            account_id="acc-1",
        )

    def test_handles_empty_transactions(self, mock_monarch_client):
        mock_monarch_client.get_transactions.return_value = {
            "allTransactions": {"results": []}
        }
        result = json.loads(get_transactions())
        assert result == []

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.get_transactions.side_effect = Exception("Auth expired")
        result = get_transactions()
        assert "Error getting transactions" in result


class TestGetBudgets:
    def test_returns_raw_budget_data(self):
        result = json.loads(get_budgets())
        assert "budgetData" in result
        categories = result["budgetData"]["monthlyAmountsByCategory"]
        assert len(categories) == 2
        assert categories[0]["category"]["name"] == "Groceries"

    def test_passes_date_params(self, mock_monarch_client):
        get_budgets(start_date="2026-03-01", end_date="2026-03-31")
        mock_monarch_client.get_budgets.assert_called_once_with(
            start_date="2026-03-01", end_date="2026-03-31"
        )

    def test_passes_none_dates_by_default(self, mock_monarch_client):
        get_budgets()
        mock_monarch_client.get_budgets.assert_called_once_with(
            start_date=None, end_date=None
        )

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.get_budgets.side_effect = Exception("Budget error")
        result = get_budgets()
        assert "Error getting budgets" in result


class TestGetCashflow:
    def test_returns_cashflow_data(self):
        result = json.loads(get_cashflow())
        assert result["cashflow"]["income"] == 5000.00
        assert result["cashflow"]["expenses"] == -3200.00

    def test_passes_date_params(self, mock_monarch_client):
        get_cashflow(start_date="2026-01-01", end_date="2026-01-31")
        mock_monarch_client.get_cashflow.assert_called_once_with(
            start_date="2026-01-01", end_date="2026-01-31"
        )

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.get_cashflow.side_effect = Exception("Cashflow error")
        result = get_cashflow()
        assert "Error getting cashflow" in result


class TestGetAccountHoldings:
    def test_returns_holdings(self):
        result = json.loads(get_account_holdings("acc-1"))
        assert result["holdings"][0]["name"] == "VTI"
        assert result["holdings"][0]["value"] == 25000.00

    def test_passes_account_id(self, mock_monarch_client):
        get_account_holdings("acc-99")
        mock_monarch_client.get_account_holdings.assert_called_once_with("acc-99")

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.get_account_holdings.side_effect = Exception("Not found")
        result = get_account_holdings("bad-id")
        assert "Error getting account holdings" in result


class TestAuthenticationHardening:
    def test_requires_manual_auth_instead_of_env_login(self, monkeypatch):
        monkeypatch.setattr(
            server_module.secure_session, "get_authenticated_client", lambda: None
        )
        monkeypatch.setenv("MONARCH_EMAIL", "user@example.com")
        monkeypatch.setenv("MONARCH_PASSWORD", "secret")

        class UnexpectedMonarchMoney:
            def __init__(self, *args, **kwargs):
                raise AssertionError("env-based login should not run")

        monkeypatch.setattr(server_module, "MonarchMoney", UnexpectedMonarchMoney)

        with pytest.raises(RuntimeError, match="Authentication needed"):
            asyncio.run(get_monarch_client())

    def test_check_auth_status_is_generic_when_authenticated(self, monkeypatch):
        monkeypatch.setattr(server_module.secure_session, "load_token", lambda: "token")
        monkeypatch.setenv("MONARCH_EMAIL", "user@example.com")

        result = check_auth_status()

        assert "configured" in result.lower()
        assert "user@example.com" not in result
        assert "keyring" not in result.lower()
        assert "token found" not in result.lower()

    def test_check_auth_status_hides_internal_errors(self, monkeypatch):
        def raise_error():
            raise RuntimeError("boom")

        monkeypatch.setattr(server_module.secure_session, "load_token", raise_error)

        result = check_auth_status()

        assert "unavailable" in result.lower()
        assert "boom" not in result
        assert "traceback" not in result.lower()


class TestWriteAccessDisabled:
    def test_create_transaction_disabled(self, mock_monarch_client):
        result = create_transaction(
            date="2026-03-15",
            account_id="acc-1",
            amount=-25.00,
            merchant_name="Coffee Shop",
            category_id="cat-1",
        )
        assert "Write access disabled" in result
        mock_monarch_client.create_transaction.assert_not_called()

    def test_update_transaction_disabled(self, mock_monarch_client):
        result = update_transaction("txn-1", category_id="cat-2")
        assert "Write access disabled" in result
        mock_monarch_client.update_transaction.assert_not_called()

    def test_set_transaction_tags_disabled(self, mock_monarch_client):
        result = set_transaction_tags("txn-1", ["tag-1"])
        assert "Write access disabled" in result
        mock_monarch_client.set_transaction_tags.assert_not_called()

    def test_add_transaction_tag_disabled(self, mock_monarch_client):
        result = add_transaction_tag("txn-1", "tag-2")
        assert "Write access disabled" in result
        mock_monarch_client.get_transaction_details.assert_not_called()
        mock_monarch_client.set_transaction_tags.assert_not_called()

    def test_create_transaction_tag_disabled(self, mock_monarch_client):
        result = create_transaction_tag("new", "#0000ff")
        assert "Write access disabled" in result
        mock_monarch_client.create_transaction_tag.assert_not_called()

    def test_categorize_transaction_disabled(self, mock_monarch_client):
        result = categorize_transaction("txn-1", "cat-2")
        assert "Write access disabled" in result
        mock_monarch_client.update_transaction.assert_not_called()

    def test_create_transaction_category_disabled(self, mock_monarch_client):
        result = create_transaction_category("grp-1", "Coffee")
        assert "Write access disabled" in result
        mock_monarch_client.create_transaction_category.assert_not_called()

    def test_refresh_accounts_disabled(self, mock_monarch_client):
        result = refresh_accounts()
        assert "Write access disabled" in result
        mock_monarch_client.request_accounts_refresh.assert_not_called()


@pytest.mark.usefixtures("enable_writes")
class TestCreateTransaction:
    def test_creates_transaction(self):
        result = json.loads(
            create_transaction(
                date="2026-03-15",
                account_id="acc-1",
                amount=-25.00,
                merchant_name="Coffee Shop",
                category_id="cat-1",
            )
        )
        assert "createTransaction" in result

    def test_passes_all_params(self, mock_monarch_client):
        create_transaction(
            date="2026-03-15",
            account_id="acc-1",
            amount=-25.00,
            merchant_name="Coffee Shop",
            category_id="cat-1",
            notes="Morning coffee",
            update_balance=True,
        )
        mock_monarch_client.create_transaction.assert_called_once_with(
            date="2026-03-15",
            account_id="acc-1",
            amount=-25.00,
            merchant_name="Coffee Shop",
            category_id="cat-1",
            notes="Morning coffee",
            update_balance=True,
        )

    def test_omits_optional_params_when_not_set(self, mock_monarch_client):
        create_transaction(
            date="2026-03-15",
            account_id="acc-1",
            amount=-25.00,
            merchant_name="Store",
            category_id="cat-1",
        )
        mock_monarch_client.create_transaction.assert_called_once_with(
            date="2026-03-15",
            account_id="acc-1",
            amount=-25.00,
            merchant_name="Store",
            category_id="cat-1",
        )

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.create_transaction.side_effect = Exception("Bad request")
        result = create_transaction(
            date="2026-03-15",
            account_id="acc-1",
            amount=-25.00,
            merchant_name="Store",
            category_id="cat-1",
        )
        assert "Error creating transaction" in result


@pytest.mark.usefixtures("enable_writes")
class TestUpdateTransaction:
    def test_updates_transaction(self):
        result = json.loads(update_transaction("txn-1", category_id="cat-2"))
        assert "updateTransaction" in result

    def test_passes_only_provided_fields(self, mock_monarch_client):
        update_transaction("txn-1", amount=99.99, notes="Updated")
        mock_monarch_client.update_transaction.assert_called_once_with(
            transaction_id="txn-1", amount=99.99, notes="Updated"
        )

    def test_passes_all_fields(self, mock_monarch_client):
        update_transaction(
            "txn-1",
            category_id="cat-2",
            merchant_name="New Merchant",
            goal_id="goal-1",
            amount=50.00,
            date="2026-04-01",
            hide_from_reports=True,
            needs_review=False,
            notes="All fields",
        )
        mock_monarch_client.update_transaction.assert_called_once_with(
            transaction_id="txn-1",
            category_id="cat-2",
            merchant_name="New Merchant",
            goal_id="goal-1",
            amount=50.00,
            date="2026-04-01",
            hide_from_reports=True,
            needs_review=False,
            notes="All fields",
        )

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.update_transaction.side_effect = Exception("Not found")
        result = update_transaction("bad-id")
        assert "Error updating transaction" in result


class TestGetTransactionCategories:
    def test_returns_categories(self):
        result = json.loads(get_transaction_categories())
        assert len(result) == 2
        assert result[0]["id"] == "cat-1"
        assert result[0]["name"] == "Groceries"
        assert result[0]["group"] == "Food"

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.get_transaction_categories.side_effect = Exception("boom")
        result = get_transaction_categories()
        assert "Error getting transaction categories" in result


class TestGetTransactionTags:
    def test_returns_tags(self):
        result = json.loads(get_transaction_tags())
        assert len(result) == 2
        assert result[0]["id"] == "tag-1"
        assert result[0]["name"] == "business"
        assert result[0]["color"] == "#ff0000"

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.get_transaction_tags.side_effect = Exception("boom")
        result = get_transaction_tags()
        assert "Error getting transaction tags" in result


@pytest.mark.usefixtures("enable_writes")
class TestSetTransactionTags:
    def test_sets_tags(self):
        result = json.loads(set_transaction_tags("txn-1", ["tag-1", "tag-2"]))
        assert "setTransactionTags" in result

    def test_passes_args(self, mock_monarch_client):
        set_transaction_tags("txn-1", ["tag-1"])
        mock_monarch_client.set_transaction_tags.assert_called_once_with(
            transaction_id="txn-1", tag_ids=["tag-1"]
        )

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.set_transaction_tags.side_effect = Exception("boom")
        result = set_transaction_tags("txn-1", [])
        assert "Error setting transaction tags" in result


@pytest.mark.usefixtures("enable_writes")
class TestCreateTransactionTag:
    def test_creates_tag(self):
        result = json.loads(create_transaction_tag("new", "#0000ff"))
        assert "createTransactionTag" in result

    def test_passes_args(self, mock_monarch_client):
        create_transaction_tag("vacation", "#00ff00")
        mock_monarch_client.create_transaction_tag.assert_called_once_with(
            name="vacation", color="#00ff00"
        )

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.create_transaction_tag.side_effect = Exception("boom")
        result = create_transaction_tag("x", "#fff")
        assert "Error creating transaction tag" in result


@pytest.mark.usefixtures("enable_writes")
class TestCategorizeTransaction:
    def test_categorizes(self, mock_monarch_client):
        result = json.loads(categorize_transaction("txn-1", "cat-2"))
        assert "updateTransaction" in result
        mock_monarch_client.update_transaction.assert_called_once_with(
            transaction_id="txn-1", category_id="cat-2"
        )

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.update_transaction.side_effect = Exception("boom")
        result = categorize_transaction("txn-1", "cat-2")
        assert "Error categorizing transaction" in result


class TestGetTransactionCategoryGroups:
    def test_returns_groups(self):
        result = json.loads(get_transaction_category_groups())
        assert len(result) == 2
        assert result[0]["id"] == "grp-1"
        assert result[0]["name"] == "Food"
        assert result[0]["type"] == "expense"

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.get_transaction_category_groups.side_effect = Exception(
            "boom"
        )
        result = get_transaction_category_groups()
        assert "Error getting transaction category groups" in result


@pytest.mark.usefixtures("enable_writes")
class TestCreateTransactionCategory:
    def test_creates_category(self):
        result = json.loads(create_transaction_category("grp-1", "Coffee"))
        assert "createCategory" in result

    def test_passes_required_args(self, mock_monarch_client):
        create_transaction_category("grp-1", "Coffee")
        mock_monarch_client.create_transaction_category.assert_called_once_with(
            group_id="grp-1", transaction_category_name="Coffee"
        )

    def test_passes_optional_args(self, mock_monarch_client):
        create_transaction_category(
            "grp-1", "Coffee", icon="☕", rollover_enabled=True, rollover_type="monthly"
        )
        mock_monarch_client.create_transaction_category.assert_called_once_with(
            group_id="grp-1",
            transaction_category_name="Coffee",
            icon="☕",
            rollover_enabled=True,
            rollover_type="monthly",
        )

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.create_transaction_category.side_effect = Exception("boom")
        result = create_transaction_category("grp-1", "Coffee")
        assert "Error creating transaction category" in result


@pytest.mark.usefixtures("enable_writes")
class TestAddTransactionTag:
    def test_appends_to_existing_tags(self, mock_monarch_client):
        result = json.loads(add_transaction_tag("txn-1", "tag-2"))
        assert "setTransactionTags" in result
        mock_monarch_client.set_transaction_tags.assert_called_once_with(
            transaction_id="txn-1", tag_ids=["tag-1", "tag-2"]
        )

    def test_no_duplicate_when_already_present(self, mock_monarch_client):
        add_transaction_tag("txn-1", "tag-1")
        mock_monarch_client.set_transaction_tags.assert_called_once_with(
            transaction_id="txn-1", tag_ids=["tag-1"]
        )

    def test_handles_no_existing_tags(self, mock_monarch_client):
        mock_monarch_client.get_transaction_details.return_value = {
            "getTransaction": {"id": "txn-1", "tags": []}
        }
        add_transaction_tag("txn-1", "tag-2")
        mock_monarch_client.set_transaction_tags.assert_called_once_with(
            transaction_id="txn-1", tag_ids=["tag-2"]
        )

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.get_transaction_details.side_effect = Exception("boom")
        result = add_transaction_tag("txn-1", "tag-2")
        assert "Error adding transaction tag" in result


@pytest.mark.usefixtures("enable_writes")
class TestRefreshAccounts:
    def test_refreshes_accounts(self):
        result = json.loads(refresh_accounts())
        assert result["requestAccountsRefresh"]["success"] is True

    def test_handles_api_error(self, mock_monarch_client):
        mock_monarch_client.request_accounts_refresh.side_effect = Exception("Timeout")
        result = refresh_accounts()
        assert "Error refreshing accounts" in result
