"""OAuth Authorization Code + PKCE support for Binance Agent OS MCP."""

from __future__ import annotations

import base64
import hashlib
import secrets
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Mapping, Optional
from urllib.parse import urlencode

import requests


ISSUER = "https://agent.binance.com"
AUTHORIZATION_ENDPOINT = "https://accounts.binance.com/agentic-oauth/authorize"
TOKEN_ENDPOINT = "https://accounts.binance.com/oauth-agentic/token"


class OAuthConfigurationError(RuntimeError):
    pass


class OAuthExchangeError(RuntimeError):
    pass


@dataclass(frozen=True)
class OAuthToken:
    access_token: str
    token_type: str
    expires_at: Optional[float]
    scope: Optional[str] = None

    @classmethod
    def from_response(cls, payload: Mapping[str, Any]) -> "OAuthToken":
        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise OAuthExchangeError("OAuth token response has no access_token")
        expires_in = payload.get("expires_in")
        expires_at = time.time() + float(expires_in) if expires_in is not None else None
        return cls(
            access_token=access_token,
            token_type=str(payload.get("token_type", "Bearer")),
            expires_at=expires_at,
            scope=str(payload["scope"]) if payload.get("scope") is not None else None,
        )

    def is_expired(self, leeway_seconds: float = 30.0) -> bool:
        return self.expires_at is not None and time.time() >= self.expires_at - leeway_seconds


class InMemoryTokenStore:
    """Process-local storage; intentionally avoids plaintext persistence."""

    def __init__(self) -> None:
        self._token: Optional[OAuthToken] = None
        self._lock = Lock()

    def get(self) -> Optional[OAuthToken]:
        with self._lock:
            return self._token

    def set(self, token: OAuthToken) -> None:
        with self._lock:
            self._token = token

    def clear(self) -> None:
        with self._lock:
            self._token = None

    def access_token(self) -> Optional[str]:
        token = self.get()
        if token is None or token.is_expired():
            return None
        return token.access_token


def generate_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


class BinanceOAuthClient:
    def __init__(
        self,
        client_id: str,
        redirect_uri: str,
        session: Optional[requests.Session] = None,
        timeout: float = 20.0,
    ) -> None:
        if not client_id or not redirect_uri:
            raise OAuthConfigurationError("BINANCE_MCP_CLIENT_ID and redirect URI are required")
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.session = session or requests.Session()
        self.timeout = timeout

    def authorization_url(self, state: str, code_challenge: str, scope: Optional[str] = None) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        if scope:
            params["scope"] = scope
        return f"{AUTHORIZATION_ENDPOINT}?{urlencode(params)}"

    def exchange_code(self, code: str, code_verifier: str) -> OAuthToken:
        response = self.session.post(
            TOKEN_ENDPOINT,
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "code": code,
                "code_verifier": code_verifier,
            },
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise OAuthExchangeError(f"Binance OAuth token exchange failed: HTTP {response.status_code}") from exc
        payload = response.json()
        if not isinstance(payload, Mapping):
            raise OAuthExchangeError("OAuth token response must be a JSON object")
        return OAuthToken.from_response(payload)
