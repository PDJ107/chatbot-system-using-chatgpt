import openai
import configparser


class ChatGPT:
    def __init__(self, config_path='resources/config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        openai.organization = config['OPENAI']['ORG']
        openai.api_key = config['OPENAI']['API_KEY']

        # self.pre_prompt = config['OPENAI']['PRE_PROMPT']
        # self.post_prompt = config['OPENAI']['POST_PROMPT']
        self.prompt = config['OPENAI']['PROMPT']
        self.system_prompt = config['OPENAI']['INIT_SYSTEM']
        self.compress_prompt = config['OPENAI']['COMPRESS_PROMPT']

    def answering_the_question(
            self,
            question: str,
            history: list,
            contexts=None,
            model="gpt-3.5-turbo",
            max_len=1200,
            size="ada",
            max_tokens=512,
            stop_sequence=None,
            debug=False
    ):
        try:
            assert history[0]['role'] == 'system'

            # context switching
            if contexts is not None:
                history[0] = eval(self.system_prompt)
                history[0]['content'] = history[0]['content'].replace('{prompt}', self.prompt)
                history[0]['content'] = history[0]['content'].replace('{context}', contexts)

            request = [{
                'role': 'user',
                'content': question
            }]

            if debug:
                print(history + request)

            response = openai.ChatCompletion.create(
                model=model,
                messages=history + request,
                temperature=0,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop_sequence,
            )

            request.append({
                'role': 'assistant',
                'content': response['choices'][0]['message']['content'].strip()
            })
            return history + request, response['choices'][0]['message']['content'].strip()

        except Exception as e:
            print(e)
            return history, ''

    def compress_context(self, question, context, max_len=300):
        prompt = self.compress_prompt
        prompt = prompt.replace('{length}', str(max_len))
        #prompt = prompt.replace('{question}', question)
        prompt = prompt.replace('{context}', context)

        try:
            response = openai.Completion.create(
                prompt=prompt,
                temperature=0,
                max_tokens=512,
                frequency_penalty=0,
                presence_penalty=0,
                model='text-davinci-003',
            )
            return response["choices"][0]["text"].strip()

        except Exception as e:
            print(e)
            return ""


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../resources/config.ini')
    history = eval(config['OPENAI']['INIT_MESSAGE'])

    reader = ChatGPT('../resources/config.ini')

    print('1. Answering')
    print(
        reader.answering_the_question(
            "너는 누구야?",
            history,
            debug=True
        )[1]
    )

    print('2. Compress')
    print(
        reader.compress_context(
            "OpenAI 플랫폼에 회원가입 후, 무료사용법 혹은 유료 구독제(ChatGPT Plus)로 이용할 수 있으며, 회원가입을 하고, 채팅을 하듯이 챗봇에 질문을 입력하는 것만으로 AI를 이용할 수 있다. 스마트폰으로도 OpenAI 플랫폼에 들어가면 이용할 수 있다. 여기서 입력하는 대화문을 '프롬프트(Prompt)'라고 하며, 이에 대한 AI의 답변을 '응답(Response)' 생성된다고 표현한다. 각 대화방의 이름은 대화를 하자마자 첫 질문과 답변에 맞게 생성되지만, 언제든지 변경할 수 있다. 2023년 3월 14일, OpenAI의 최신 언어모델인 GPT-4가 출시되었으며, 현재 ChatGPT Plus 가입자만 사용할 수 있다."
        )
    )