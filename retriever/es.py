import configparser
from elasticsearch import Elasticsearch, exceptions


class ES:
    def __init__(self, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = Elasticsearch(config['ES']['URL'], request_timeout=60 * 1)
        self.init_messages = eval(config['OPENAI']['INIT_MESSAGE'])

    def get_context(self, query, index, k=2):
        query = {
            "multi_match": {
              "query": query,
            }
        }
        response = self.es.search(index=index,
                                  query=query,
                                  size=k).body

        if response['_shards']['total'] == 0:
            return []
        return [context['_source']['contents'] for context in response['hits']['hits']]

    def get_history(self, user_id):

        try:
            return self.es.get(index='messages', id=user_id)['_source']['messages']

        except exceptions.NotFoundError:

            print("Not Found")
            return self.init_history(user_id)

    def update_history(self, user_id, messages):
        doc = {
            'messages': messages
        }

        try:
            self.es.update(index='messages', id=user_id, doc=doc)

        except exceptions.NotFoundError:

            print("Not Found")
            self.es.index(index='messages', id=user_id, document=doc)

    def init_history(self, user_id):
        init_doc = {
            'messages': self.init_messages
        }

        self.es.index(index='messages', id=user_id, document=init_doc)
        return init_doc['messages']

    def input_data(self, contexts, index):
        for context in contexts:
            self.es.index(index=index, document=context)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../config.ini')

    es = ES('../config.ini')
    print(es.get_context('한기대 개교일', config['RETRIEVER']['INDEX'], k=1))

