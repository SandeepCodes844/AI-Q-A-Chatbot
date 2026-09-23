import os

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

app = FastAPI()

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    raise RuntimeError("SARVAM_API_KEY is not set. Add it to your .env file.")

client = SarvamAI(
    api_subscription_key=api_key
)


def get_sarvam_response(messages):
    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=messages,
        temperature=0.2,
        top_p=1,
        max_tokens=2000,
    )
    return response.choices[0].message.content


class Question(BaseModel):
    question: str


# Store the old conversation summary
summary = ""

# Store the recent conversation
history = []

# Create a summary after 6 messages
MAX_MESSAGES = 6


@app.post("/chat")
def chat(data: Question):
    global summary, history

    history.append({
        "role": "user",
        "content": data.question
    })

    messages = []
    if summary:
        messages.append({
            "role": "system",
            "content": f"Conversation summary:\n{summary}"
        })

    messages.extend(history)

    answer = get_sarvam_response(messages)

    history.append({
        "role": "assistant",
        "content": answer
    })

    if len(history) >= MAX_MESSAGES:
        summary_prompt = [{
            "role": "system",
            "content": (
                "Summarize the conversation briefly. "
                "Keep only important information needed "
                "to continue the conversation."
            )
        }]

        if summary:
            summary_prompt.append({
                "role": "user",
                "content": f"Previous summary:\n{summary}"
            })

        conversation = ""
        for message in history:
            conversation += f"{message['role']}: {message['content']}\n"

        summary_prompt.append({
            "role": "user",
            "content": f"Conversation:\n{conversation}"
        })

        summary = get_sarvam_response(summary_prompt)
        history = []

    return {"answer": answer}