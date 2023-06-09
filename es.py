import configparser
from elasticsearch import Elasticsearch, exceptions
from dto.user.user import User
from dacite import from_dict


class ES:
    def __init__(self, config_path='resources/config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = Elasticsearch(config['ES']['URL'], request_timeout=60 * 1)
        self.init_messages = eval(config['OPENAI']['INIT_MESSAGE'])
        self.init_user = eval(config['ES']['INIT_USER'])

    def get_client(self):
        return self.es

    def get_user(self, user_id) -> User:

        try:
            data = self.es.get(index='users', id=user_id)['_source']
            return from_dict(data_class=User, data=data)

        except exceptions.NotFoundError:

            print("Not Found")
            self.init_user['user_id'] = user_id
            self.es.index(index='users', document=self.init_user, id=user_id)
            return from_dict(data_class=User, data=self.init_user)

    def update_user(self, user_id, user: dict):

        try:
            self.es.update(index='users', id=user_id, doc=user)

        except exceptions.NotFoundError:

            print("Not Found")
            self.es.index(index='users', id=user_id, document=user)

    def get_context(self, query, index, k=2) -> (list, list):
        query = {
            "multi_match": {
              "query": query,
            }
        }
        response = self.es.search(index=index,
                                  query=query,
                                  size=k).body

        if response['_shards']['total'] == 0:
            return [], []

        context_list = [context['_source']['contents'] for context in response['hits']['hits']]
        source = [context['_source']['link'] for context in response['hits']['hits']]
        return context_list, list(set(source))

    def get_memory(self, user_id) -> str:

        try:
            return self.es.get(index='memories', id=user_id)['_source']['memory']

        except exceptions.NotFoundError:

            print("Not Found")
            return self.init_memory(user_id)

    def update_memory(self, user_id, memory_pickle: str):
        doc = {
            'memory': memory_pickle
        }

        try:
            self.es.update(index='memories', id=user_id, doc=doc)

        except exceptions.NotFoundError:

            print("Not Found")
            self.es.index(index='memories', id=user_id, document=doc)

    def init_memory(self, user_id) -> str:
        init_doc = {
            'memory': ''
        }

        self.es.index(index='memories', id=user_id, document=init_doc)
        return ''

    def input_data(self, contexts: list, index: str):
        for context in contexts:
            self.es.index(index=index, document=context)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../resources/config.ini')

    es = ES('resources/config.ini')
    print(es.get_context('한기대 개교일', config['RETRIEVER']['INDEX'], k=1))

