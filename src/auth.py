from __future__ import annotations

import http.server
import json
import logging
import socketserver
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import requests

from .models import SpotifyCredentials, TokenData


logger = logging.getLogger(__name__)

# Constants
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-top-read"
TOKEN_CACHE_FILE = Path.home() / ".spotify_token_cache.json"


class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    auth_code: str | None = None

    def do_GET(self) -> None:
        params = parse_qs(urlparse(self.path).query)

        if "code" in params:
            CallbackHandler.auth_code = params["code"][0]
            self._send_response(200, "Authorization successful! You can close this window.")
        else:
            self._send_response(400, "Authorization failed!")

    def _send_response(self, status: int, message: str) -> None:
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = f"<html><body><h1>{message}</h1></body></html>"
        self.wfile.write(html.encode())

    def log_message(self, format: str, *args) -> None:
        pass


class SpotifyAuth:
    def __init__(self, credentials: SpotifyCredentials):
        self.credentials = credentials

    def get_access_token(self) -> str:
        cached_token = self._load_cached_token()

        if cached_token and cached_token.refresh_token:
            try:
                logger.info("Using cached credentials...")
                return self._refresh_token(cached_token.refresh_token)
            except requests.HTTPError as e:
                logger.warning(f"Token refresh failed: {e}. Re-authenticating...")

        return self._authenticate()

    def _authenticate(self) -> str:
        auth_code = self._get_authorization_code()
        token_data = self._exchange_code_for_token(auth_code)
        self._save_token(token_data)
        return token_data.access_token

    def _get_authorization_code(self) -> str:
        auth_params = {
            "client_id": self.credentials.client_id,
            "response_type": "code",
            "redirect_uri": self.credentials.redirect_uri,
            "scope": SCOPE,
        }

        auth_url = f"{AUTH_URL}?{urlencode(auth_params)}"
        logger.info("Opening browser for authorization...")
        logger.info(f"If browser doesn't open, visit: {auth_url}")
        webbrowser.open(auth_url)

        port = urlparse(self.credentials.redirect_uri).port or 8888
        CallbackHandler.auth_code = None

        with socketserver.TCPServer(("", port), CallbackHandler) as httpd:
            httpd.handle_request()

        if not CallbackHandler.auth_code:
            raise RuntimeError("Failed to get authorization code")

        return CallbackHandler.auth_code

    def _exchange_code_for_token(self, code: str) -> TokenData:
        headers = {
            "Authorization": f"Basic {self.credentials.get_auth_header()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.credentials.redirect_uri,
        }

        response = requests.post(TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()

        return TokenData.from_dict(response.json())

    def _refresh_token(self, refresh_token: str) -> str:
        headers = {
            "Authorization": f"Basic {self.credentials.get_auth_header()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        response = requests.post(TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()

        token_data = TokenData.from_dict(response.json())
        if not token_data.refresh_token:
            token_data.refresh_token = refresh_token

        self._save_token(token_data)
        return token_data.access_token

    @staticmethod
    def _load_cached_token() -> TokenData | None:
        if not TOKEN_CACHE_FILE.exists():
            return None

        try:
            with TOKEN_CACHE_FILE.open("r") as f:
                data = json.load(f)
                return TokenData.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    @staticmethod
    def _save_token(token_data: TokenData) -> None:
        with TOKEN_CACHE_FILE.open("w") as f:
            json.dump(token_data.to_dict(), f)
