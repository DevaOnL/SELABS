"""A music catalog and playlist manager for a streaming service."""

import json
import random
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE songs ("
    "id INTEGER PRIMARY KEY, title TEXT, artist TEXT, plays INTEGER)"
)


def add_song(title, artist, plays=0, playlist=None):
    """Add a song to the catalog and append its title to a playlist."""
    if playlist is None:
        playlist = []
    conn.execute(
        "INSERT INTO songs (title, artist, plays) VALUES (?, ?, ?)",
        (title, artist, plays),
    )
    playlist.append(title)
    return playlist


def shuffle_pick():
    """Return the id of a randomly chosen song from the catalog."""
    ids = [row[0] for row in conn.execute("SELECT id FROM songs")]
    return random.choice(ids)  # nosec B311 - not used for security purposes


def popularity(title):
    """Rate a song as popular or niche based on its play count."""
    row = conn.execute(
        "SELECT plays FROM songs WHERE title = ?", (title,)
    ).fetchone()
    if row is None:
        return "unknown"
    return "popular" if row[0] > 100 else "niche"


def save_playlist(playlist):
    """Serialize a playlist into a JSON string."""
    return json.dumps(playlist)


def load_playlist(blob):
    """Rebuild a playlist from a JSON string."""
    return json.loads(blob)


def total_plays():
    """Return the total play count of all songs, or 0 on a database error."""
    try:
        return conn.execute("SELECT SUM(plays) FROM songs").fetchone()[0]
    except sqlite3.Error:
        return 0


def main():
    """Run a short demonstration of the catalog."""
    playlist = add_song("Aurora", "Nila", 250)
    add_song("Monsoon", "Kavya", 40, playlist)
    blob = save_playlist(playlist)
    loaded = load_playlist(blob)
    if len(loaded) > 1:
        print("multi-song playlist")
    print(
        popularity("Aurora"),
        popularity("Monsoon"),
        shuffle_pick(),
        total_plays(),
    )


if __name__ == "__main__":
    main()
