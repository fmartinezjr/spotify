from __future__ import annotations

import argparse
import logging
import sys

import requests

from .auth import SpotifyAuth
from .client import SpotifyClient, TimeRange
from .models import SpotifyCredentials


logger = logging.getLogger(__name__)


def display_tracks(tracks: list[dict], time_range: TimeRange, limit: int) -> None:
    print(f"\n{'=' * 80}")
    print(f"YOUR TOP {limit} SONGS ({time_range.replace('_', ' ').upper()})")
    print(f"{'=' * 80}\n")

    for idx, track in enumerate(tracks, 1):
        artists = ", ".join(artist["name"] for artist in track["artists"])
        print(f"{idx:2d}. {track['name']}")
        print(f"    Artist(s): {artists}")
        print(f"    Album: {track['album']['name']}")
        print(f"    Popularity: {track['popularity']}/100")
        print(f"    URL: {track['external_urls']['spotify']}")
        print()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Get your top Spotify tracks")
    parser.add_argument(
        "--time-range",
        choices=["short_term", "medium_term", "long_term"],
        default="medium_term",
        help="Time range: short_term (4 weeks), medium_term (6 months), long_term (all time)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of tracks to display (max 50)",
    )

    args = parser.parse_args()

    try:
        credentials = SpotifyCredentials.from_env()
    except ValueError as e:
        logger.error(f"Error: {e}")
        logger.info("\nTo get credentials:")
        logger.info("1. Go to https://developer.spotify.com/dashboard")
        logger.info("2. Create an app")
        logger.info("3. Copy the Client ID and Client Secret")
        logger.info("4. Set redirect URI to http://127.0.0.1:8888/callback")
        return 1

    try:
        auth = SpotifyAuth(credentials)
        client = SpotifyClient(auth)
        tracks = client.get_top_tracks(args.time_range, args.limit)
        display_tracks(tracks, args.time_range, args.limit)
        return 0
    except requests.HTTPError as e:
        logger.error(f"API error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
