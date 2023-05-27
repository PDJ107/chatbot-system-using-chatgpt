import configparser
from reader.chatgpt import ChatGPT

class Retriever:
    def __init__(self, es, google_api, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = es
        self.google_api = google_api
        self.index = config['RETRIEVER']['INDEX']

    def get_context(self, question, chatgpt: ChatGPT, max_len=256, k=2):
        query = ' | '.join(
            self.question_preprocessing(question)
        )

        # elastic search
        contexts = self.es.get_context(query, self.index, k)

        # google api
        # contexts.append(
        #     self.google_api.get_context(question, size=1)
        # )

        for i, context in [(i, c) for (i, c) in enumerate(contexts)]:
            if len(context) >= max_len:
                contexts[i] = self.compress_context(context)

        contexts = self.context_postprocessing(
            contexts
        )
        print(contexts)
        return contexts

    def question_preprocessing(self, question):
        return question

    def context_postprocessing(self, contexts: list, max_len=1024):
        contexts = '\n\n---\n\n'.join(contexts)
        return contexts[:max_len]

    def compress_context(self, context, chatgpt: ChatGPT):
        return chatgpt.compress_context(context)