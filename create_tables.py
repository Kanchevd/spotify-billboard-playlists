import sqlite3


# songs  - id INTEGER PRIMARY KEY, name TEXT, uri TEXT
# charts - id INTEGER PRIMARY KEY, name TEXT, link TEXT, desc TEXT, playlist_id TEXT, archive_name TEXT, archive desc TEXT, archive_playlist_id TEXT
# songs_in_charts = song_id, chart_id
def create_tables():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY, name TEXT NOT NULL, uri TEXT NOT NULL, last_week_updated:)")
    cur.execute("CREATE TABLE IF NOT EXISTS charts(id INTEGER PRIMARY KEY, name TEXT NOT NULL, link TEXT NOT NULL, playlist_id TEXT, "
                "archive_playlist_id TEXT)")
    con.commit()
    con.close()


if __name__ == '__main__':
    create_tables()
