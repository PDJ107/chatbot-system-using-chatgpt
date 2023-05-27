import configparser
from elasticsearch import exceptions
from reader.chatgpt import ChatGPT
from retriever.es import ES


class Reader:
    def __init__(self, es: ES, chatgpt: ChatGPT, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = es
        self.reader = chatgpt

        self.init_messages = eval(config['OPENAI']['INIT_MESSAGE'])

    def answering_the_question(self, user_id, question, contexts=""):
        new_history, answer = self.reader.answering_the_question(
            question,
            self.get_history(user_id),
            contexts
        )

        self.update_history(user_id, new_history)
        return answer

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