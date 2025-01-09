import sqlite3

def create_table():
    connection = sqlite3.connect("songs.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist TEXT NOT NULL,
            title TEXT NOT NULL,
            lyrics TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


def insert_song(artist, title, lyrics):
    connection = sqlite3.connect("songs.db")
    cursor = connection.cursor()


    cursor.execute("""
        SELECT * FROM songs WHERE artist = ? AND title = ?
    """, (artist, title))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("""
            INSERT INTO songs (artist, title, lyrics) VALUES (?, ?, ?)
        """, (artist, title, lyrics))
        connection.commit()

    connection.close()


def get_all_songs():
    connection = sqlite3.connect("songs.db")
    cursor = connection.cursor()

    cursor.execute("SELECT artist, title, lyrics FROM songs")
    songs = cursor.fetchall()

    connection.close()
    return songs


def delete_all_songs():
    connection = sqlite3.connect("songs.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM songs")
    connection.commit()

    connection.close()
