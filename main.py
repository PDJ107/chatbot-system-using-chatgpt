import uvicorn
from fastapi import FastAPI, BackgroundTasks
import configparser
from pydantic import BaseModel
from agent import Agent
from messages import SpecificFCM
from tools.es import ES
import requests
from urllib.parse import urljoin
import firebase_admin
from firebase_admin import credentials


class Question(BaseModel):
    question: str
    user_id: str
    fcm_token: str


class Request(BaseModel):
    user_id: str
    fcm_token: str


config = configparser.ConfigParser()
config.read('resources/config.ini')

app = FastAPI()

es = ES()
cred = credentials.Certificate(config['FCM']['KEY_PATH'])
firebase_admin.initialize_app(cred)
#chatgpt = ChatGPT()
#reader = Reader(es, chatgpt)
#retriever = Retriever(es, chatgpt)
#fcm = FCM()


def finish_answer(user_id):
    url = urljoin(config['ETC']['MAIN_URL'], 'chat/v1/status')
    data = {
        'user_id': user_id,
        'isAnswering': 0
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.put(url, json=data, headers=headers)
    print(data)
    print(url, response)


def request_answer(request: Question):
    print("Question: ", request.question)
    fcm = SpecificFCM(request.fcm_token)
    agent = Agent(
        client=es.get_client(),
        index_name=config['RETRIEVER']['INDEX'],
        memory_pickle=es.get_memory(request.user_id),
        message_client=fcm
    )
    try:
        _, memory_pickle = agent.run(request.question)
        es.update_memory(request.user_id, memory_pickle)  # update history
    except Exception:
        fcm.send_message(config['OPENAI']['FAILED'])

    finish_answer(request.user_id)  # 답변 완료 알림


def request_init_history(request: Request):
    es.init_memory(request.user_id)
    SpecificFCM(request.fcm_token).send_message('대화 기록 초기화 완료')
    finish_answer(request.user_id)  # 답변 완료 알림


def request_source(request: Request):
    #user = es.get_user(request.user_id)
    #fcm.send_message('\n'.join(user.context_source), request.fcm_token)

    finish_answer(request.user_id)  # 답변 완료 알림


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chatbot", status_code=202)
async def chat(request: Question, background_tasks: BackgroundTasks):
    background_tasks.add_task(request_answer, request)
    return {"message": "답변 요청 완료"}


@app.post("/chatbot/init", status_code=202)
def init_context(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(request_init_history, request)
    return {"message": "초기화 요청 완료"}


@app.post("/chatbot/source", status_code=202)
def get_source(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(request_source, request)
    return {"message": "출처 요청 완료"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
