import uvicorn
from fastapi import FastAPI, BackgroundTasks
import configparser
from pydantic import BaseModel
from retriever.es import ES
from retriever.retriever import Retriever
from reader.chatgpt import ChatGPT
from reader.reader import Reader
from fcm import Fcm
from dataclasses import dataclass, asdict
import requests
import json
from urllib.parse import urljoin


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
chatgpt = ChatGPT()
reader = Reader(es, chatgpt)
retriever = Retriever(es, chatgpt)
fcm = Fcm()


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
    # 1. context switching 체크
    user = es.get_user(request.user_id)
    query, context_switching = retriever.check_context(request.question, user.user_id)

    # 2. context 검색
    if user.context is False or context_switching:
        fcm.send_message('Context switching...', request.fcm_token)
        contexts = retriever.get_context(
            user,
            query=query,
            question=request.question
        )
        user.context = True
        es.update_user(user.user_id, asdict(user))

    else:
        contexts = None

    # 3. 답변 생성
    fcm.send_message('답변 생성중...', request.fcm_token)
    answer = reader.answering_the_question(
        request.user_id,
        question=request.question,
        contexts=contexts
    )
    fcm.send_message(answer, request.fcm_token)

    # 4. 답변 완료 상태 업데이트
    finish_answer(user.user_id)


def request_init_context(request: Request):
    es.init_history(request.user_id)
    fcm.send_message('Context 초기화 완료', request.fcm_token)

    # 답변 완료 상태 업데이트
    finish_answer(request.user_id)


def request_source(request: Request):
    user = es.get_user(request.user_id)
    fcm.send_message('\n'.join(user.context_source), request.fcm_token)

    # 답변 완료 상태 업데이트
    finish_answer(request.user_id)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chatbot", status_code=202)
async def chat(request: Question, background_tasks: BackgroundTasks):
    background_tasks.add_task(request_answer, request)
    return {"message": "답변 요청 완료"}


@app.post("/chatbot/init", status_code=202)
def init_context(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(request_init_context, request)
    return {"message": "초기화 요청 완료"}


@app.post("/chatbot/source", status_code=202)
def get_source(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(request_source, request)
    return {"message": "출처 요청 완료"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
