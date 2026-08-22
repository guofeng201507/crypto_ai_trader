import time
from urllib.parse import parse_qs, urlparse

import pytest

from binance_agent_os.oauth import (
    AUTHORIZATION_ENDPOINT,
    BinanceOAuthClient,
    InMemoryTokenStore,
    OAuthExchangeError,
    OAuthToken,
    TOKEN_ENDPOINT,
    generate_pkce,
)


class TokenResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {"access_token": "secret", "token_type": "Bearer", "expires_in": 3600}


class TokenSession:
    def __init__(self):
        self.calls = []

    def post(self, url, data, timeout):
        self.calls.append((url, data, timeout))
        return TokenResponse()


def test_pkce_and_authorization_url():
    verifier, challenge = generate_pkce()
    assert verifier
    assert "=" not in challenge
    client = BinanceOAuthClient("client-id", "http://127.0.0.1/callback")
    url = client.authorization_url("state", challenge)
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == AUTHORIZATION_ENDPOINT
    assert query["response_type"] == ["code"]
    assert query["code_challenge_method"] == ["S256"]


def test_exchange_code_uses_verified_token_endpoint():
    session = TokenSession()
    token = BinanceOAuthClient(
        "client-id", "http://127.0.0.1/callback", session=session
    ).exchange_code("code", "verifier")
    assert session.calls[0][0] == TOKEN_ENDPOINT
    assert session.calls[0][1]["grant_type"] == "authorization_code"
    assert token.access_token == "secret"


def test_token_store_rejects_expired_token():
    store = InMemoryTokenStore()
    store.set(OAuthToken("secret", "Bearer", time.time() - 1))
    assert store.access_token() is None


def test_token_response_requires_access_token():
    with pytest.raises(OAuthExchangeError):
        OAuthToken.from_response({})
