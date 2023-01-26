import requests
import spotipy
from lxml import html
from requests.exceptions import ReadTimeout
from spotipy.oauth2 import SpotifyOAuth

import config

chartList = [{"link": "https://www.billboard.com/charts/hot-100/", "playlistID": "0q8fbu1LEBfJB58LawLyLc", "name": "Hot 100"}, {
    "link": "https://www.billboard.com/charts/billboard-global-200/", "playlistID": "2jrKsIhIQMwaoZPjs25hpD", "name": "Global 200"}]


def spotifyAuth():
    scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.client_id,
                         client_secret=config.client_secret, redirect_uri='https://example.com/callback/', scope=scope))

    return sp


def sanitizeAuthor(artist):
    stringsToRemove = [' Featuring ', ' X ',
                       ' & ', ' And ', ' x ', ' / ', ', ', ' + ']
    for string in stringsToRemove:
        artist = artist.replace(string, ' ')
    return artist


def getChartData(chartInfo):
    page = requests.get(chartInfo["link"])
    tree = html.fromstring(page.text)
    chartInfo["week"] = tree.xpath("//p[contains(.,'Week of ')]/text()")[0][8:]
    chartInfo["songs"] = []

    songElements = tree.xpath(
        "//li[contains(@class, 'o-chart-results-list__item')][h3]")
    for song in songElements:
        artist = song.xpath('./span/text()')[0].strip()
        songName = song.xpath('./h3/text()')[0].strip()
        artist = sanitizeAuthor(artist)
        chartInfo["songs"].append({
            'name': songName,
            'artist': artist
        })

    return chartInfo


def getSongIDs(sp, songs):
    songIds = []
    for song in songs:
        searchTerm = f"{song['name']} {song['artist']}"
        try:
            songIds.append(sp.search(q=searchTerm, type="track", limit=1)[
                'tracks']['items'][0]['id'])
        except ReadTimeout:
            print('Spotify timed out... trying again...')
            songIds.append(sp.search(q=searchTerm, type="track", limit=1)[
                'tracks']['items'][0]['id'])

    return songIds


def updatePlaylists(sp, playlistID, songIds):
    sp.playlist_replace_items(
        playlist_id=playlistID, items=songIds[:100])
    del songIds[:100]
    while songIds:
        sp.playlist_add_items(
            playlist_id=playlistID, items=songIds[:100])
        del songIds[:100]


def updateDescription(sp, chart):
    desc = f'Welcome to the weekly Billboard {chart["name"]} chart ranking! Updated automatically every week. Maintained by Daniel Kanchev. Current Week: {chart["week"]}.'
    sp.playlist_change_details(
        playlist_id=chart["playlistID"], description=desc)


def updateCharts():
    sp = spotifyAuth()
    chartData = [getChartData(chart) for chart in chartList]

    for chart in chartData:
        songIds = getSongIDs(sp, chart["songs"])
        updatePlaylists(sp, chart["playlistID"], songIds)
        updateDescription(sp, chart)


if __name__ == "__main__":
    updateCharts()
