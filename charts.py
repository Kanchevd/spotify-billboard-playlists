import sqlite3

import requests
from lxml import html


class Charts:
    @staticmethod
    def get_database_cursor():
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        return con.cursor()

    @staticmethod
    def get_chart_name_from_link(link):
        cur = Charts.get_database_cursor()
        cur.execute("SELECT name FROM charts WHERE link=?", (link,))
        return cur.fetchone()['name']

    @staticmethod
    def get_current_chart_week(link):
        page = requests.get(link)
        tree = html.fromstring(page.text)
        current_week = tree.xpath("//p[contains(.,'Week of ')]/text()")[0][8:]
        return current_week

    @staticmethod
    def get_billboard_chart(link):
        page = requests.get(link)
        tree = html.fromstring(page.text)
        song_elements = tree.xpath("//li[contains(@class, 'o-chart-results-list__item')][h3]")
        songs = []
        position = 1
        week = Charts.get_current_chart_week(link)
        chart_name = Charts.get_chart_name_from_link(link)
        stuff_to_remove = ['Featuring', 'X', '&', 'And', 'x', '/']
        for element in song_elements:
            artist = element.xpath('./span/text()')[0].strip()
            for string in stuff_to_remove:
                short_artist = artist.split(f' {string} ')[0] or ''
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
        cur = Charts.get_database_cursor()
        cur.execute("SELECT link FROM charts")
        chart_list = [x['link'] for x in cur.fetchall()]
        for chart in chart_list:
            print(Charts.get_billboard_chart(chart))


if __name__ == "__main__":
    Charts.get_all_charts()
