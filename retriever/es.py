import configparser
from elasticsearch import Elasticsearch, exceptions


class ES:
    def __init__(self, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = Elasticsearch(config['ES']['URL'], request_timeout=60 * 1)

        print(self.es.info().body)

    def get_context(self, query, index, k=2):
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
    config = configparser.ConfigParser()
    config.read('../config.ini')

    es = ES('../config.ini')
    print(es.get_context('한기대 개교일', config['RETRIEVER']['INDEX'], k=1))

