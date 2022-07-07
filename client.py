import sqlite3

import tekore

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

        user_token = tekore.prompt_for_user_token(
            self.client_id,
            self.client_secret,
            self.redirect_uri,
            scope=tekore.scope.every)
        self.spotify.token = user_token

    def update_playlist_from_song_list(self, playlist_id, songs):
        uris = self.songs_to_uris(songs)
        self.spotify.playlist_clear(playlist_id)
        self.add_songs_to_playlist(uris=uris, playlist_id=playlist_id)

    def get_playlist_songs(self, playlist_id):
        all_tracks = []
        offset = 0
        tracks = [item['track']['uri'] for item in self.spotify.playlist_items(playlist_id, as_tracks=True)['items']]
        all_tracks.extend(tracks)
        while len(tracks) == 100:
            offset += 100
            tracks = [item['track']['uri'] for item in
                      self.spotify.playlist_items(playlist_id, as_tracks=True, offset=offset)['items']]
            if tracks:
                all_tracks.extend(tracks)
        return all_tracks

    def add_songs_to_playlist(self, uris, playlist_id):
        while uris:
            if len(uris) > 100:
                self.spotify.playlist_add(playlist_id=playlist_id, uris=uris[:100])
                uris = uris[100:]
            else:
                self.spotify.playlist_add(playlist_id=playlist_id, uris=uris)
                uris = []

    def songs_to_uris(self, songs):
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("SELECT name, uri FROM songs")
        uri_dict = dict(cur.fetchall())
        uris = []
        new_songs = {}
        for song in songs:
            full_name = f"{song['name']} {song['artist']}"
            short_name = song['name']
            if full_name not in uri_dict.keys():
                track = self.spotify.search(full_name, types=('track',))[0]
                if not track.items:
                    print(f"no track found for full name:{full_name}")
                    track = self.spotify.search(short_name, types=('track',))[0]
                    if track.items:
                        uri = track.items[0].uri
                        new_songs[short_name] = uri
                    else:
                        print(f"no track found for short name:{full_name}")
                        uri = "29c0d880f5494b34"  # Song's name is "Doesn't exist"
                else:
                    uri = track.items[0].uri
                    new_songs[full_name] = uri
            else:
                uri = uri_dict[full_name]
            uris.append(uri)

        if new_songs:
            print(f"{len(new_songs)} new songs!")
            for song_name in new_songs:
                cur.execute("INSERT INTO songs(name, uri) VALUES (?,?)", (song_name, new_songs[song_name]))
            con.commit()

        con.close()
        return uris

    def update_current_charts(self):
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM charts")
        charts = cur.fetchall()
        con.close()
        for chart in charts:
            current_week = get_current_chart_week(link=chart['link'])
            if current_week == chart['last_updated']:
                print(f'{chart["name"]} is up to date.')
                continue
            self.update_playlist_from_song_list(playlist_id=chart['playlist_id'],
                                                songs=get_billboard_chart(chart['link']))
            self.spotify.playlist_change_details(playlist_id=chart['playlist_id'],
                                                 description=f"The current {chart['name']} chart, updated automatically. "
                                                             f"Current Week: {current_week}. Created by: Daniel Kanchev.")
            self.extend_archive_playlist(playlist_id=chart['playlist_id'],
                                         archive_playlist_id=chart['archive_playlist_id'])
            self.spotify.playlist_change_details(playlist_id=chart['archive_playlist_id'],
                                                 description=f"All songs that have charted on the {chart['name']}"
                                                             f"in 2022 updated automatically. "
                                                             f"Current Week: {current_week}. Created by: Daniel Kanchev.")
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            cur.execute("UPDATE charts SET last_updated = ? WHERE id = ?", (current_week, chart['id']))
            con.commit()
            con.close()
            print(f'{chart["name"]} is updated.')


if __name__ == "__main__":
    client = SpotifyClient()
