from __future__ import annotations

from services.api.client.accounts import AccountsClient

def test_accounts_client_search_params() -> None:
    assert hasattr(AccountsClient, "list_accounts")
