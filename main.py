import tekore
import config
import sqlite3
import requests
from lxml import html


def get_billboard_chart(link):
    page = requests.get(link)
    tree = html.fromstring(page.text)
    song_elements = tree.xpath("//li[contains(@class, 'o-chart-results-list__item')][h3]")
    songs = []
    stuff_to_remove = ['Featuring', 'X', '&', 'And', 'x', '/']
    for element in song_elements:
        artist = element.xpath('./span/text()')[0].strip()
        for string in stuff_to_remove:
            artist = artist.split(f' {string} ')[0]
        songs.append({
            'name': element.xpath('./h3/text()')[0].strip(),
            'artist': artist
        })
    return songs


def current_chart_week(link):
    page = requests.get(link)
    tree = html.fromstring(page.text)
    current_week = tree.xpath("//p[contains(.,'Week of ')]/text()")[0][8:]
    return current_week


class SpotifyClient:
    def __init__(self, auth=True):
        self.app_token = tekore.request_client_token(config.client_id, config.client_secret)
        self.spotify = tekore.Spotify(self.app_token)
        if auth:
            redirect_uri = 'https://example.com/callback'
            user_token = tekore.prompt_for_user_token(
                config.client_id,
                config.client_secret,
                redirect_uri,
                scope=tekore.scope.every)
            self.spotify.token = user_token

    def update_playlist_from_song_list(self, playlist_id, songs):
        uris = self.songs_to_uris(songs)
        self.spotify.playlist_clear(playlist_id)
        self.add_songs_to_playlist(uris=uris, playlist_id=playlist_id)

    def extend_archive_playlist(self, playlist_id, archive_playlist_id):
        current_tracks_uris = self.get_playlist_songs(playlist_id)
        archive_uris = self.get_playlist_songs(archive_playlist_id)

        uris_to_archive = []
        for uri in current_tracks_uris:
            if uri not in archive_uris:
                uris_to_archive.append(uri)
        self.add_songs_to_playlist(uris=uris_to_archive, playlist_id=archive_playlist_id)

    def get_playlist_songs(self, playlist_id):
        all_tracks = []
        offset = 0
        tracks = [item['track']['uri'] for item in self.spotify.playlist_items(playlist_id, as_tracks=True)['items']]
        all_tracks.extend(tracks)
        while len(tracks) == 100:
            offset += 100
            tracks = [item['track']['uri'] for item in self.spotify.playlist_items(playlist_id, as_tracks=True, offset=offset)['items']]
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
            current_week = current_chart_week(link=chart['link'])
            if current_week == chart['last_updated']:
                print(f'{chart["name"]} is up to date.')
                continue
            self.update_playlist_from_song_list(playlist_id=chart['playlist_id'], songs=get_billboard_chart(chart['link']))
            self.spotify.playlist_change_details(playlist_id=chart['playlist_id'], description=f"The current {chart['name']} chart, updated automatically. "
                                                                                               f"Current Week: {current_week}. Created by: Daniel Kanchev.")
            self.extend_archive_playlist(playlist_id=chart['playlist_id'], archive_playlist_id=chart['archive_playlist_id'])
            self.spotify.playlist_change_details(playlist_id=chart['archive_playlist_id'], description=f"All songs that have charted on the {chart['name']}"
                                                                                                       f"in 2022 updated automatically. "
                                                                                                       f"Current Week: {current_week}. Created by: Daniel Kanchev.")
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            cur.execute("UPDATE charts SET last_updated = ? WHERE id = ?", (current_week, chart['id']))
            con.commit()
            con.close()
            print(f'{chart["name"]} is updated.')


if __name__ == '__main__':
    client = SpotifyClient()
    client.update_current_charts()
