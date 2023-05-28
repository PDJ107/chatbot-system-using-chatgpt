import configparser
from reader.chatgpt import ChatGPT
from retriever.google_api import GoogleApi
from retriever.es import ES

from konlpy.tag import Mecab

class Retriever:
    def __init__(self, es: ES, chatgpt: ChatGPT, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = es
        self.chatgpt = chatgpt
        self.google_api = GoogleApi(config_path)

        self.mecab = Mecab()

        self.index = config['RETRIEVER']['INDEX']

    def get_context(self, question, max_len=256, k=2):
        query = self.question_preprocessing(question)
        print('extract nouns: ', query)

        contexts = []

        # elastic search
        contexts += self.es.get_context(query, self.index, k=k)

        # google api
        contexts += self.google_api.get_context(question, size=k)
        print(contexts)
        for i, context in [(i, c) for (i, c) in enumerate(contexts)]:
            if len(context) >= max_len:
                contexts[i] = self.chatgpt.compress_context(question, context[:1700], max_len)

        context = self.context_postprocessing(
            contexts
        )
        print(context)
        return context

    def question_preprocessing(self, question):
        query = []
        for word, pos in self.mecab.pos(question):
            for target in ['SN', 'N']:
                if pos.startswith(target):
                    query.append(word)
                    break

        return ' '.join(query)

    def context_postprocessing(self, contexts: list, max_len=1024):
        contexts = '\n---\n'.join(contexts)
        return contexts[:max_len]

