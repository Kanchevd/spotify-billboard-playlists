"""Main function which chains functionality together."""
from charts import Charts
from client import SpotifyClient
from create_tables import create_tables


def main():
    """Main function which chains functionality together."""
    if not Charts.update_needed():
        print("Charts are up to date.")
        return

    print("New charts available!")
    create_tables()
    songs = Charts.get_all_charts()
    client = SpotifyClient()
    for song in songs:
        song['uri'] = client.find_song_uri(song['name'], song['artists'])

    Charts.write_to_db(songs)
    client.update_current_charts()


if __name__ == "__main__":
    main()
