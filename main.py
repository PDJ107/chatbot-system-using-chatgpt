import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from retriever.es import ES
from retriever.retriever import Retriever
from reader.chatgpt import ChatGPT
from reader.reader import Reader


class Question(BaseModel):
    question: str
    user_id: str


class Request(BaseModel):
    user_id: str


app = FastAPI()

es = ES()
chatgpt = ChatGPT()

reader = Reader(es, chatgpt)
retriever = Retriever(es, chatgpt)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chatbot")
def get_answer(request: Question):
    context = retriever.get_context(
        question=request.question
    )
    answer = reader.answering_the_question(
        request.user_id,
        question=request.question,
        contexts=context
    )
    return {'answer': answer}


@app.post("/chatbot/init")
def init_context(request: Request):
    es.init_history(request.user_id)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
