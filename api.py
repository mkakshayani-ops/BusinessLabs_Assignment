from fastapi import FastAPI
from pydantic import BaseModel

from chatbot import ask
from brain import retrieve

app = FastAPI(
    title="Knowledge Brain",
    description="Answers questions from the Brilliant Directories help center, with sources.",
)


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    """Quick check that the service is running."""
    return {"status": "ok"}


@app.post("/ask")
def ask_endpoint(body: Question):
    """Answer a question. Returns the answer, its sources, and whether a human is needed."""
    return ask(body.question)


@app.post("/search")
def search_endpoint(body: Question):
    """Return the raw evidence without calling the language model (cheap and fast)."""
    return retrieve(body.question)