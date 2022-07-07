"""
Scrapes all Billboard charts present in the database and adds their entries to the relevant tables.
"""
import sqlite3

import requests
from lxml import html


class Charts:
    """
    Manages Billboard charts and their entries.
    """

    @staticmethod
    def get_database_cursor():
        """Creates a cursor for database operations."""
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        return con.cursor()

    @staticmethod
    def get_chart_name_from_link(link):
        """Gets the name of a Billboard chart from the URL of the chart."""
        cur = Charts.get_database_cursor()
        cur.execute("SELECT name FROM charts WHERE link=?", (link,))
        return cur.fetchone()['name']

    @staticmethod
    def get_current_chart_week(link):
        """Gets the current week of the chart."""
        page = requests.get(link)
        tree = html.fromstring(page.text)
        current_week = tree.xpath("//p[contains(.,'Week of ')]/text()")[0][8:]
        return current_week

    @staticmethod
    def get_billboard_chart(link):
        """Generates all new Billboard entries for a given chart and adds them to a database."""
        page = requests.get(link)
        tree = html.fromstring(page.text)
        song_elements = tree.xpath("//li[contains(@class, 'o-chart-results-list__item')][h3]")

        songs = []
        position = 1
        week = Charts.get_current_chart_week(link)
        chart_name = Charts.get_chart_name_from_link(link)

        bad_strings = [' Featuring ', ' X ', ' & ', ' And ', ' x ', ' / ']

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
                'short_artist': short_artist or '',
                'position': position,
                'week': week,
                'chart': chart_name
            })
            position += 1

        return songs

    @staticmethod
    def get_all_charts():
        """Executes an update for all charts in the database."""
        cur = Charts.get_database_cursor()
        cur.execute("SELECT link FROM charts")
        chart_list = [x['link'] for x in cur.fetchall()]
        for chart in chart_list:
            print(Charts.get_billboard_chart(chart))


if __name__ == "__main__":
    Charts.get_all_charts()
