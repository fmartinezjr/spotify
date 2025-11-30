# Spotify Top Songs

Get  top listened songs from Spotify.


## Setup

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Command

```bash
python spotify_top_songs.py
```

With options:
```bash
python3 spotify_top_songs.py --time-range short_term --limit 50
```

### Options

- `--time-range`: Choose from:
  - `short_term` - Last 4 weeks
  - `medium_term` - Last 6 months (default)
  - `long_term` - All time

- `--limit`: Number of tracks to display (1-50, default: 20)

## Examples

```bash
# Top 10 tracks from the last month
python spotify_top_songs.py --time-range short_term --limit 10

# Top 50 tracks of all time
python spotify_top_songs.py --time-range long_term --limit 50
```
