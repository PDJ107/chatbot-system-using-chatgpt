import configparser
from elasticsearch import Elasticsearch
from pprint import pprint


class ES:
    def __init__(self, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = Elasticsearch(config['ES']['URL'], request_timeout=60*1)
        self.index = config['ES']['INDEX']

        pprint(self.es.info().body)

    def getContext(self, query, size=3):
        return self.es.search(index='context-v1',
                              query={
                                  'multi_match': {
                                      'query': query,
                                      'fields': ['*']
                                  }
                              },
                              size=size).body


if __name__ == '__main__':
    retriever = ES('../config.ini')
    pprint(retriever.getContext('한기대 개교일은?', 1))

