#!/usr/bin/env python3
"""
Script to fetch Last.fm data and update _data/music.yml

Usage:
    python scripts/update_music_data.py

Requirements:
    pip install requests pyyaml

Environment variables:
    LASTFM_API_KEY - Your Last.fm API key (get one at https://www.last.fm/api/account/create)
    LASTFM_USERNAME - Last.fm username to fetch data for (default: jaimeum19)
"""

import os
import requests
import yaml
from datetime import datetime

# Configuration
LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
LASTFM_USERNAME = os.environ.get("LASTFM_USERNAME", "jaimeum19")
BASE_URL = "http://ws.audioscrobbler.com/2.0/"


def api_call(method: str, **params) -> dict:
    """Make a Last.fm API call."""
    params.update({
        "method": method,
        "api_key": LASTFM_API_KEY,
        "format": "json",
    })
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()


def get_user_info(username: str) -> dict:
    """Get user profile information."""
    data = api_call("user.getinfo", user=username)
    return data.get("user", {})


def get_top_artists(username: str, period: str = "overall", limit: int = 5) -> list:
    """Get user's top artists."""
    data = api_call("user.gettopartists", user=username, period=period, limit=limit)
    return data.get("topartists", {}).get("artist", [])


def get_top_tracks(username: str, period: str = "overall", limit: int = 5) -> list:
    """Get user's top tracks."""
    data = api_call("user.gettoptracks", user=username, period=period, limit=limit)
    return data.get("toptracks", {}).get("track", [])


def get_top_albums(username: str, period: str = "overall", limit: int = 5) -> list:
    """Get user's top albums."""
    data = api_call("user.gettopalbums", user=username, period=period, limit=limit)
    return data.get("topalbums", {}).get("album", [])


def get_recent_tracks(username: str, limit: int = 5) -> list:
    """Get user's recent tracks."""
    data = api_call("user.getrecenttracks", user=username, limit=limit)
    return data.get("recenttracks", {}).get("track", [])


def format_number(num: str | int) -> str:
    """Format a number with commas."""
    return f"{int(num):,}"


def generate_music_yaml(username: str) -> str:
    """Generate the music.yml content from Last.fm data."""
    print(f"Fetching data for user: {username}")
    
    # Fetch all data
    user_info = get_user_info(username)
    top_artists = get_top_artists(username, limit=5)
    top_tracks = get_top_tracks(username, limit=5)
    top_albums = get_top_albums(username, limit=5)
    recent_tracks = get_recent_tracks(username, limit=5)
    
    # Build the YAML structure
    music_data = []
    
    # Listening Statistics
    stats = {
        "key": "Listening Statistics",
        "value": [
            {"key": "Total Scrobbles", "value": format_number(user_info.get("playcount", 0))},
            {"key": "Last.fm Profile", "value": username, "url": user_info.get("url", f"https://www.last.fm/user/{username}")},
        ]
    }
    music_data.append(stats)
    
    # Top Artists
    if top_artists:
        artists = {
            "key": "Top Artists",
            "value": [
                {
                    "key": f"#{i+1}",
                    "value": f"{artist['name']} ({format_number(artist['playcount'])} plays)",
                    "url": artist.get("url", "")
                }
                for i, artist in enumerate(top_artists)
            ]
        }
        music_data.append(artists)
    
    # Top Tracks
    if top_tracks:
        tracks = {
            "key": "Top Tracks",
            "value": [
                {
                    "key": f"#{i+1}",
                    "value": f"{track['name']} - {track['artist']['name']}",
                    "url": track.get("url", "")
                }
                for i, track in enumerate(top_tracks)
            ]
        }
        music_data.append(tracks)
    
    # Top Albums
    if top_albums:
        albums = {
            "key": "Top Albums",
            "value": [
                {
                    "key": f"#{i+1}",
                    "value": f"{album['name']} - {album['artist']['name']}",
                    "url": album.get("url", "")
                }
                for i, album in enumerate(top_albums)
            ]
        }
        music_data.append(albums)
    
    # Recently Played
    if recent_tracks:
        recent = {
            "key": "Recently Played",
            "value": [
                {
                    "key": f"#{i+1}",
                    "value": f"{track['name']} - {track['artist'].get('#text', track['artist'])}",
                    "url": track.get("url", "")
                }
                for i, track in enumerate(recent_tracks[:5])
            ]
        }
        music_data.append(recent)
    
    # Return link
    music_data.append({
        "key": "return",
        "value": "previous page",
        "url": "https://jaimeum.github.io"
    })
    
    return yaml.dump(music_data, default_flow_style=False, allow_unicode=True, sort_keys=False)


def main():
    if not LASTFM_API_KEY:
        print("Error: LASTFM_API_KEY environment variable is not set.")
        print("Get an API key at: https://www.last.fm/api/account/create")
        return 1
    
    yaml_content = generate_music_yaml(LASTFM_USERNAME)
    
    # Write to _data/music.yml
    output_path = os.path.join(os.path.dirname(__file__), "..", "_data", "music.yml")
    output_path = os.path.normpath(output_path)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    
    print(f"Successfully updated {output_path}")
    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0


if __name__ == "__main__":
    exit(main())
