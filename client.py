"""Contains operations requiring access to a Spotify Account"""

import tekore

from charts import Charts
from db_operations import create_connection
from load_config import load_config


class SpotifyClient:
    """Represents a connection to a specific spotify account and contains the associated operations."""
    app_token = None
    spotify = None
    config = load_config()
    client_id = config['client']['client_id']
    client_secret = config['client']['client_secret']
    redirect_uri = 'https://example.com/callback'

    def __init__(self):
        self.app_token = tekore.request_client_token(self.client_id, self.client_secret)
        self.spotify = tekore.Spotify(self.app_token)

        con = create_connection()
        cur = con.cursor()
        tokens = cur.execute("SELECT * FROM properties WHERE property IN ('access_token', 'refresh_token') "
                             "ORDER BY property ASC").fetchall()
        if tokens:
            access_token = tokens[0]['val']
            print("access_token:", access_token)
            refresh_token = tokens[1]['val']
            print("refresh_token:", refresh_token)
            try:
                self.spotify.token = access_token
                self.spotify.playback_currently_playing()
                print("Valid token found!")
            except tekore.Unauthorised:
                print("Invalid token found!")
                cred = tekore.Credentials(self.client_id, self.client_secret, self.redirect_uri)
                new_token = cred.refresh_user_token(refresh_token=refresh_token)
                self.spotify.token = new_token
                self.spotify.playback_currently_playing()
                SpotifyClient.update_access_token(new_token.access_token)
        else:
            print("No token found, initiating prompt..")
            new_token = tekore.prompt_for_user_token(
                self.client_id,
                self.client_secret,
                self.redirect_uri,
                scope=tekore.scope.every)
            self.spotify.token = new_token
            SpotifyClient.write_token(new_token)

    @staticmethod
    def write_token(token: tekore.RefreshingToken):
        con = create_connection()
        cur = con.cursor()
        cur.execute("INSERT INTO properties(property, val) VALUES (?, ?)",
                    ('access_token', token.access_token))
        cur.execute("INSERT INTO properties(property, val) VALUES (?, ?)",
                    ('refresh_token', token.refresh_token))
        con.commit()
        con.close()

    @staticmethod
    def update_access_token(access_token):
        con = create_connection()
        cur = con.cursor()
        print(access_token)
        print(type(access_token))
        cur.execute("UPDATE properties SET val = ? WHERE property = access_token",
                    (access_token,))
        con.commit()
        con.close()

    @staticmethod
    def get_chart_playlist_id(chart):
        con = create_connection()
        cur = con.cursor()

        playlist_id = cur.execute("SELECT playlist_id FROM charts WHERE name = ?", (chart,)).fetchone()['playlist_id']

        con.close()
        return playlist_id

    def update_chart(self, chart, current_week):

        con = create_connection()
        cur = con.cursor()
        songs = cur.execute("SELECT song_id FROM chart_entries WHERE chart = ? AND week = ?"
                            "ORDER BY position ASC", (chart, current_week)).fetchall()
        song_ids = [song['song_id'] for song in songs]
        uris = []
        for song_id in song_ids:
            uris.append(cur.execute("SELECT uri FROM songs WHERE id = ?", (song_id,)).fetchone()['uri'])

        con.close()
        playlist_id = self.get_chart_playlist_id(chart)
        self.spotify.playlist_clear(playlist_id)
        self.add_songs_to_playlist(uris=uris, playlist_id=playlist_id)
        con.close()

    def add_songs_to_playlist(self, uris, playlist_id):
        while uris:
            if len(uris) > 100:
                self.spotify.playlist_add(playlist_id=playlist_id, uris=uris[:100])
                uris = uris[100:]
            else:
                self.spotify.playlist_add(playlist_id=playlist_id, uris=uris)
                uris = []

    def find_song_uri(self, song, artists):
        search_term = f"{song} {' '.join(artists)}"
        track = self.spotify.search(search_term, types=('track',))[0]
        if track.items:
            return track.items[0].uri

        return f"No track found for search term:{search_term}"

    def update_current_charts(self):
        con = create_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM charts")
        charts = cur.fetchall()
        con.close()
        for chart in charts:
            current_week = Charts.get_current_chart_week()

            self.update_chart(chart['name'], current_week)
            self.spotify.playlist_change_details(playlist_id=chart['playlist_id'],
                                                 description=f"The current {chart['name']} chart, "
                                                             f"updated automatically. "
                                                             f"Current Week: {current_week}. "
                                                             f"Created by: Daniel Kanchev.")

            con = create_connection()
            cur = con.cursor()
            cur.execute("UPDATE properties SET val = ? WHERE property = 'current_week'", (current_week,))
            con.commit()
            con.close()
            print(f'{chart["name"]} is updated.')


if __name__ == "__main__":
    client = SpotifyClient()
