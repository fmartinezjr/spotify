from __future__ import annotations

import base64
from dataclasses import dataclass


@dataclass
class SpotifyCredentials:
    client_id: str
    client_secret: str
    redirect_uri: str = "http://127.0.0.1:8888/callback"

    @classmethod
    def from_env(cls) -> SpotifyCredentials:
        import os

        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "Missing credentials. Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET"
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", cls.__dataclass_fields__['redirect_uri'].default),
        )

    def get_auth_header(self) -> str:
        credentials = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(credentials.encode()).decode()


@dataclass
class TokenData:
    access_token: str
    refresh_token: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> TokenData:
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
        )

    def to_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }
