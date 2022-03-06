import tekore as tk
from scrape_billboard import get_billboard_chart
import config

app_token = tk.request_client_token(config.client_id, config.client_secret)
spotify = tk.Spotify(app_token)

redirect_uri = 'https://example.com/callback'
user_token = tk.prompt_for_user_token(
    config.client_id,
    config.client_secret,
    redirect_uri,
    scope=tk.scope.every
)
spotify.token = user_token


def get_playlist_id_from_name(playlist_name):
    playlist_id = 0
    for playlist in spotify.playlists(config.user_id).items:
        if playlist.name == playlist_name:
            playlist_id = playlist.id
            break
    return playlist_id


def update_playlist_from_song_list(playlist_name, songs):
    playlist_id = get_playlist_id_from_name(playlist_name)
    if not playlist_id:
        print("No such playlist found")
        return
    print('playlist found')
    uris = songs_to_uris(songs)
    print('got uris')
    spotify.playlist_clear(playlist_id)
    add_all_uris_to_playlist(uris=uris, playlist_id=playlist_id)


def extend_archive_playlist(archive_name, current_playlist_name):
    archive_playlist_id = get_playlist_id_from_name(archive_name)
    if not archive_playlist_id:
        print("No archive playlist found")
        return
    current_playlist_id = get_playlist_id_from_name(current_playlist_name)
    if not current_playlist_id:
        print("No current playlist found")
        return
    current_tracks_uris = retrieve_all_songs_from_playlist(current_playlist_id)
    archive_uris = retrieve_all_songs_from_playlist(archive_playlist_id)
    print(len(current_tracks_uris))
    print(len(archive_uris))
    uris_to_archive = []
    for uri in current_tracks_uris:
        if uri not in archive_uris:
            uris_to_archive.append(uri)
    add_all_uris_to_playlist(uris=uris_to_archive, playlist_id=archive_playlist_id)


def retrieve_all_songs_from_playlist(playlist_id):
    all_tracks = []
    offset = 0
    tracks = [item['track']['uri'] for item in spotify.playlist_items(playlist_id, as_tracks=True)['items']]
    all_tracks.extend(tracks)
    while len(tracks) == 100:
        offset += 100
        tracks = [item['track']['uri'] for item in spotify.playlist_items(playlist_id, as_tracks=True, offset=offset)['items']]
        if tracks:
            all_tracks.extend(tracks)
    return all_tracks


def add_all_uris_to_playlist(uris, playlist_id):
    while uris:
        if len(uris) > 100:
            spotify.playlist_add(playlist_id=playlist_id, uris=uris[:100])
            uris = uris[100:]
        else:
            spotify.playlist_add(playlist_id=playlist_id, uris=uris)
            uris = []


def songs_to_uris(songs):
    uris = []
    for song in songs:
        tracks = spotify.search(f"{song['name']} {song['artist']}", types=('track',))
        if not tracks[0].items:
            print(f"no track found for {song['name']} {song['artist']}")
            tracks = spotify.search(f"{song['name']}", types=('track',))
        uris.append(tracks[0].items[0].uri)
    return uris


def update_current_charts():
    update_playlist_from_song_list(config.global_200_name, songs=get_billboard_chart(config.global_200_link))
    update_playlist_from_song_list(config.hot_100_name, songs=get_billboard_chart(config.hot_100_link))


def extend_archive_charts():
    extend_archive_playlist(archive_name=config.hot_100_archive_name, current_playlist_name=config.hot_100_name)
    extend_archive_playlist(archive_name=config.global_200_archive_name, current_playlist_name=config.global_200_name)


if __name__ == '__main__':
    update_current_charts()
    extend_archive_charts()
