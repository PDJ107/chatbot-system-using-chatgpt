import configparser
from googleapiclient.discovery import build
import re
from bs4 import BeautifulSoup
import requests


class GoogleApi:
    def __init__(self, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.id = config['GOOGLE']['SEARCH_ENGINE_ID']

        self.service = build(
            "customsearch", "v1", developerKey=config['GOOGLE']['API_KEY']
        )

    def get_context(self, query, size=1):
        contexts = []
        try:
            items = (
                self.service.cse()
                .list(
                    q=query,
                    cx=self.id,

                )
                .execute()
            )['items']

            # pprint(items)

            for i in range(min(size, len(items))):
                link = items[i]['link']
                contexts.append(
                    self.get_html(items[i]['link'], items[i]['snippet'])
                )

            return contexts

        except Exception as e:
            print(type(e), e)
            return contexts

    def get_html(self, url, snippet, max_len=1600):
        hdr = {'User-Agent': 'Mozilla/5.0'}
        html = requests.get(url, headers=hdr)

        html.encoding = 'utf-8'

        soup = BeautifulSoup(html.text, 'html.parser')
        # pprint(soup)
        elems = soup.find_all(
            name=['div', 'article', 'section', 'main']
        )

        # pprint(elems)

        context = snippet + '\n'
        for row in elems:
            if row.find(['dl', 'dt', 'dd', 'em', 'a', 'input', 'select', 'button']) is None:
                context += row.get_text(strip=True)

        if len(context) > max_len:
            new_context = context[:max_len]
            for c in context[max_len:]:
                new_context += c
                if c in ['.', '\n']: break

            context = new_context

        return context


if __name__ == '__main__':
    google = GoogleApi('../config.ini')
    print(google.get_context('chatgpt란?'))