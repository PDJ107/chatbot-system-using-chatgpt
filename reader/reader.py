import configparser
from reader.chatgpt import ChatGPT
from retriever.es import ES


class Reader:
    def __init__(self, es: ES, chatgpt: ChatGPT, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.es = es
        self.reader = chatgpt

    def answering_the_question(self, user_id, question, contexts=""):
        new_history, answer = self.reader.answering_the_question(
            question,
            self.es.get_history(user_id),
            contexts,
            debug=True
        )

        self.es.update_history(user_id, new_history)
        return answer
