import openai
import configparser


class ChatGPT:
    def __init__(self, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        openai.organization = config['OPENAI']['ORG']
        openai.api_key = config['OPENAI']['API_KEY']

        self.pre_prompt = config['OPENAI']['PRE_PROMPT']
        self.post_prompt = config['OPENAI']['POST_PROMPT']

    def answer_question(
            self,
            question,
            context="",
            model="text-davinci-003",
            max_len=1800,
            size="ada",
            max_tokens=300,
            stop_sequence=None,
    ):
        try:
            response = openai.Completion.create(
                prompt=f"{self.pre_prompt}\n\n---Context: {context}\n\n---\n\nQuestion: {question}\n\n---\n\n{self.post_prompt}\n\nAnswer: ",
                temperature=0,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop_sequence,
                model=model,
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            print(e)
            return ""


if __name__ == '__main__':
    reader = ChatGPT('../config.ini')
    print(
        reader.answer_question("너는 누구야?")
    )