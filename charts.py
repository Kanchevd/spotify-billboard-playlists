"""
Scrapes all Billboard charts present in the database and adds their entries to the relevant tables.
"""
import re

import requests
from lxml import html

from create_db_connection import create_connection
from load_config import load_config


class Charts:
    """
    Manages Billboard charts and their entries.
    """
    config = load_config()

    @staticmethod
    def get_chart_name_from_link(link):
        """Gets the name of a Billboard chart from the URL of the chart."""
        con = create_connection()
        cur = con.cursor()

        cur.execute("SELECT name FROM charts WHERE link=?", (link,))
        chart_name = cur.fetchone()['name']

        con.close()

        return chart_name

    @staticmethod
    def extract_html_from_link(link, xpath):
        """Given a URL and xpath, extracts HTML from the URL using the xpath."""
        page = requests.get(link)
        tree = html.fromstring(page.text)
        return tree.xpath(xpath)

    @staticmethod
    def get_current_chart_week():
        """Gets the current week of the chart."""
        return Charts.extract_html_from_link('https://www.billboard.com/charts/hot-100/',
                                             "//p[contains(.,'Week of ')]/text()")[0][8:]

    @staticmethod
    def extract_artists(element):
        split_strings = [' Featuring ', ' X ', ' & ', ' And ', ' x ', ' / ', ', ', '(', ')']
        special_artists = ['Tyler, The Creator', 'Tones And I', 'Lil Nas X']
        special_artists_found = []

        artists = element.xpath('./span/text()')[0].strip()
        for special_artist in special_artists:
            if special_artist in artists:
                special_artists_found.append(special_artist)
                artists = artists.replace(special_artist, '')

        regex_pattern = '|'.join(map(re.escape, split_strings))

        artists = re.split(regex_pattern, artists)
        artists = [artist.strip() for artist in artists if artist]
        if special_artists_found:
            artists.extend(special_artists_found)

        return artists

    @staticmethod
    def get_billboard_chart(link):
        """Generates all new Billboard entries for a given chart and adds them to a database."""
        song_elements = Charts.extract_html_from_link(link, "//li[contains(@class, 'o-chart-results-list__item')][h3]")
        week = Charts.get_current_chart_week()
        chart_name = Charts.get_chart_name_from_link(link)

        songs = []
        position = 1

        for element in song_elements:
            artists = Charts.extract_artists(element)

            songs.append({
                'name': element.xpath('./h3/text()')[0].strip(),
                'artists': artists,
                'position': position,
                'week': week,
                'chart': chart_name
            })
            position += 1

        return songs

    @staticmethod
    def get_all_charts():
        """Executes an update for all charts in the database."""
        con = create_connection()
        cur = con.cursor()

        cur.execute("SELECT link FROM charts")
        chart_list = [x['link'] for x in cur.fetchall()]
        songs = []
        for chart_link in chart_list:
            songs.extend(Charts.get_billboard_chart(chart_link))

        return songs

    @staticmethod
    def update_needed():
        current_week = Charts.get_current_chart_week()
        con = create_connection()
        cur = con.cursor()
        last_updated = cur.execute("SELECT val FROM properties WHERE property='current_week'").fetchone()['val']
        con.close()
        print('Current week:', current_week)
        print('Last Updated:', last_updated)
        return current_week != last_updated


if __name__ == "__main__":
    Charts.get_all_charts()
