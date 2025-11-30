from __future__ import annotations

from typing import Literal

import requests

from .auth import SpotifyAuth


TimeRange = Literal["short_term", "medium_term", "long_term"]

TOP_TRACKS_URL = "https://api.spotify.com/v1/me/top/tracks"


class SpotifyClient:
    def __init__(self, auth: SpotifyAuth):
        self.auth = auth

    def get_top_tracks(
        self, time_range: TimeRange = "medium_term", limit: int = 50
    ) -> list[dict]:
        access_token = self.auth.get_access_token()

        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"time_range": time_range, "limit": limit}

        response = requests.get(TOP_TRACKS_URL, headers=headers, params=params)
        response.raise_for_status()

        return response.json()["items"]
