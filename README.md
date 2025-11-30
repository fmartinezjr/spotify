# Spotify Top Songs

Get your most listened songs from Spotify.


##  Install the Package
```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage
```bash
spotify-top-songs
```

### Options

- `--time-range`: Choose from:
  - `short_term` - Last 4 weeks
  - `medium_term` - Last 6 months (default)
  - `long_term` - All time

- `--limit`: Number of tracks to display (1-50, default: 20)

### Examples

```bash
# Top 10 tracks from the last month
spotify-top-songs --time-range short_term --limit 10

# Top 50 tracks of all time
spotify-top-songs --time-range long_term --limit 50

# Default: top 20 tracks from last 6 months
spotify-top-songs
```