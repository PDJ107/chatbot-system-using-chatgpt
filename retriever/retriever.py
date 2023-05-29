import configparser
from dto.user.user import User
from reader.chatgpt import ChatGPT
from retriever.google_api import GoogleApi
from retriever.es import ES
from konlpy.tag import Mecab
from dataclasses import asdict


class Retriever:
    def __init__(self, es: ES, chatgpt: ChatGPT, config_path='resources/config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = es
        self.chatgpt = chatgpt
        self.google_api = GoogleApi(config_path)

        self.mecab = Mecab()

        self.index = config['RETRIEVER']['INDEX']

    def check_context(self, question, user_id) -> (str, bool):
        query = self.question_preprocessing(question)
        prev_query = self.question_preprocessing(
            self.es.get_history(user_id)[-2]['content']
        )
        print('extract nouns: ', query)
        print('prev extract nouns: ', prev_query)

        return query, len(set(query).intersection(set(prev_query))) == 0

    def get_context(self, user: User, query: list, question: str, max_len=256, k=2):
        contexts = []
        sources = []
        query = ' '.join(query)

        # elastic search
        context_list, source = self.es.get_context(query, self.index, k=k)
        contexts += context_list
        sources += source

        # google api
        context_list, source = self.google_api.get_context('한기대 ' + question, size=k)
        contexts += context_list
        sources += source

        for i, context in [(i, c) for (i, c) in enumerate(contexts)]:
            if len(context) >= max_len:
                contexts[i] = self.chatgpt.compress_context(question, context[:1700], max_len)

        context = self.context_postprocessing(
            contexts
        )
        print(context)

        # 출처 업데이트
        user.context_source = sources
        self.es.update_user(user.user_id, asdict(user))

        return context

    def question_preprocessing(self, question) -> list:
        query = []
        for word, pos in self.mecab.pos(question):
            for target in ['SN', 'NNG']:
                if target in pos:
                    query.append(word)
                    break

        return query

    def context_postprocessing(self, contexts: list, max_len=1024):
        contexts = '\n---\n'.join(contexts)
        return contexts[:max_len]

