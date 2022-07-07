"""
Scrapes all Billboard charts present in the database and adds their entries to the relevant tables.
"""
import configparser
import sqlite3

import requests
from lxml import html


class Charts:
    """
    Manages Billboard charts and their entries.
    """
    config = None
    __instance = None

    def __init__(self):
        """ Virtually private constructor. """
        if Charts.__instance is None:
            raise Exception("This class is a singleton!")

        Charts.__instance = self
        Charts.config = Charts.load_config()

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Charts.__instance is None:
            Charts()
        return Charts.__instance

    @staticmethod
    def load_config():
        """Initializes configuration file."""
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config

    @staticmethod
    def create_connection():
        """Creates a connection for database operations and returns the cursor."""
        con = sqlite3.connect(Charts.config['database']['dbname'])
        con.row_factory = sqlite3.Row
        return con

    @staticmethod
    def get_chart_name_from_link(link):
        """Gets the name of a Billboard chart from the URL of the chart."""
        con = Charts.create_connection()
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
    def get_current_chart_week(link):
        """Gets the current week of the chart."""
        return Charts.extract_html_from_link(link, "//p[contains(.,'Week of ')]/text()")[0][8:]

    @staticmethod
    def get_billboard_chart(link):
        """Generates all new Billboard entries for a given chart and adds them to a database."""
        song_elements = Charts.extract_html_from_link(link, "//li[contains(@class, 'o-chart-results-list__item')][h3]")
        week = Charts.get_current_chart_week(link)
        chart_name = Charts.get_chart_name_from_link(link)

        songs = []
        position = 1
        bad_strings = ['Featuring', 'X', '&', 'And', 'x', '/']
        bad_strings = [f' {x} ' for x in bad_strings]

        for element in song_elements:
            artist = element.xpath('./span/text()')[0].strip()
            short_artist = artist

            if any(x in short_artist for x in bad_strings):
                for string in bad_strings:
                    short_artist = short_artist.replace(string, ' ')

                if short_artist != artist:
                    print(artist, " => ", short_artist)

            songs.append({
                'name': element.xpath('./h3/text()')[0].strip(),
                'full_artist': artist,
                'short_artist': short_artist,
                'position': position,
                'week': week,
                'chart': chart_name
            })
            position += 1

        return songs

    @staticmethod
    def get_all_charts():
        """Executes an update for all charts in the database."""
        con = Charts.create_connection()
        cur = con.cursor()

        cur.execute("SELECT link FROM charts")
        chart_list = [x['link'] for x in cur.fetchall()]
        for chart_link in chart_list:
            print(Charts.get_billboard_chart(chart_link))


if __name__ == "__main__":
    Charts.get_all_charts()
