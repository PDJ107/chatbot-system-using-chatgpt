import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from retriever.es import ES
from reader.chatgpt import ChatGPT


class Request(BaseModel):
    question: str


app = FastAPI()
retriever = ES()
reader = ChatGPT()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chatbot")
def get_answer(request: Request):
    context = '\n---\n'.join(
        retriever.get_context(
            query=request.question
        )
    )
    answer = reader.answer_question(
        question=request.question,
        context=context
    )
    return {'answer': answer}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
