"""Main function which chains functionality together."""
from charts import Charts
from client import SpotifyClient
from create_tables import create_tables
from db_write import write_to_db


def main():
    """Main function which chains functionality together."""
    create_tables()
    if not Charts.update_needed():
        print("Charts are up to date.")
        return

    print("New charts available!")
    songs = Charts.get_all_charts()
    client = SpotifyClient()
    for song in songs:
        song['uri'] = client.find_song_uri(song['name'], song['artists'])

    write_to_db(songs, client)
    client.update_current_charts()


if __name__ == "__main__":
    main()
