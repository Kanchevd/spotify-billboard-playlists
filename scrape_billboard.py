import requests
from lxml import html


def get_billboard_chart(link):
    page = requests.get(link)
    tree = html.fromstring(page.text)
    song_elements = tree.xpath("//li[contains(@class, 'o-chart-results-list__item')][h3]")
    songs = []
    for element in song_elements:
        songs.append({
            'name': element.xpath('./h3/text()')[0].strip(),
            'artist': element.xpath('./span/text()')[0].strip().replace(' Featuring ', ' ').replace(' X ', ' ').replace(' & ', ' ').replace(' And ', ' ').replace(' x ', ' ')
                .replace(' / ', ' ')
        })
    return songs


