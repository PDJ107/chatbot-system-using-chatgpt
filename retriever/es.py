import configparser
from elasticsearch import Elasticsearch
from pprint import pprint
import json


class ES:
    def __init__(self, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = Elasticsearch(config['ES']['URL'], request_timeout=60 * 1)
        self.index = config['ES']['INDEX']

        pprint(self.es.info().body)

    def get_context(self, query, index=None, k=3):
        index = self.index if index is None else index
        return self.es.search(index=index,
                              query={
                                  'multi_match': {
                                      'query': query,
                                      'fields': ['*']
                                  }
                              },
                              size=k).body

    def input_data(self, contexts, index):
        for context in contexts:
            self.es.index(index=index, document=context)


if __name__ == '__main__':
    retriever = ES('../config.ini')
    pprint(retriever.get_context('한기대 개교일은?', k=1))

