import json
import random
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE songs ("
    "id INTEGER PRIMARY KEY, title TEXT, artist TEXT, plays INTEGER)"
)


def addSong(title, artist, plays=0, playlist=[]):
    conn.execute(
        "INSERT INTO songs (title, artist, plays) VALUES (?, ?, ?)",
        (title, artist, plays),
    )
    playlist.append(title)
    return playlist


def shufflePick():
    ids = [r[0] for r in conn.execute("SELECT id FROM songs")]
    return random.choice(ids)  # nosec B311 - not used for security purposes


def popularity(title):
    row = conn.execute(
        "SELECT plays FROM songs WHERE title = ?", (title,)
    ).fetchone()
    if row is None:
        return "unknown"
    else:
        return "popular" if row[0] > 100 else "niche"


def savePlaylist(playlist):
    return json.dumps(playlist)


def loadPlaylist(blob):
    return json.loads(blob)


def totalPlays():
    try:
        return conn.execute("SELECT SUM(plays) FROM songs").fetchone()[0]
    except sqlite3.Error:
        return 0


def main():
    pl = addSong("Aurora", "Nila", 250)
    addSong("Monsoon", "Kavya", 40, pl)
    blob = savePlaylist(pl)
    loaded = loadPlaylist(blob)
    if len(loaded) > 1:
        print("multi-song playlist")
    print(
        popularity("Aurora"),
        popularity("Monsoon"),
        shufflePick(),
        totalPlays(),
    )


main()
