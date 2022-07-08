from client import SpotifyClient
from create_db_connection import create_connection


def write_to_db(songs, client):
    for song in songs:
        write_artists_to_db(song['artists'], client)
        song = write_song_to_db(song)
        write_chart_entry_to_db(song)


def write_artists_to_db(artists, client: SpotifyClient):
    con = create_connection()
    cur = con.cursor()

    new_artists = []

    for artist in artists:
        exists = cur.execute("SELECT name FROM artists WHERE name = ?", (artist,)).fetchone()
        if not exists:
            new_artists.append(artist)

    for artist in new_artists:
        uri = client.find_artist_uri(artist)
        cur.execute("INSERT INTO artists(name, uri) VALUES(?, ?)", (artist, uri))

    con.commit()
    con.close()


def write_song_to_db(song):
    con = create_connection()
    cur = con.cursor()
    exists = cur.execute("SELECT id FROM songs WHERE uri = ?", (song['uri'],)).fetchone()
    if exists:
        song['id'] = exists['id']
        return song

    cur.execute("INSERT INTO songs(name, uri) VALUES(?, ?)", (song['name'], song['uri']))
    song['id'] = cur.lastrowid
    for artist in song['artists']:
        cur.execute("INSERT INTO song_artists(song_id, artist) VALUES(?, ?)", (song['id'], artist))

    con.commit()
    con.close()

    return song


def write_chart_entry_to_db(song):
    con = create_connection()
    cur = con.cursor()
    print(song['id'])
    cur.execute("INSERT OR IGNORE INTO chart_entries(song_id, chart, week, position) VALUES(?, ?, ?, ?)",
                (song['id'], song['chart'], song['week'], song['position']))

    con.commit()
    con.close()
