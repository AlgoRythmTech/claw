from fastapi import FastAPI, Form
from pydantic import BaseModel

from secretary.config import Settings
from secretary.engine import SecretaryEngine
from secretary.memory import MemoryStore
from secretary.models import IncomingMessage

settings = Settings.from_env()
store = MemoryStore(settings.database_path)
store.upsert_contact(settings.master_number, "master", settings.master_name, "Primary authority")
engine = SecretaryEngine(settings, store)

app = FastAPI(title="Executive Secretary")


class MessageRequest(BaseModel):
    from_number: str
    body: str


@app.post("/messages")
def messages(payload: MessageRequest) -> dict:
    reply = engine.handle(IncomingMessage(sender=payload.from_number, body=payload.body))
    return {"reply": reply.text, "action": reply.action_taken}


@app.post("/webhooks/whatsapp")
def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)) -> str:
    reply = engine.handle(IncomingMessage(sender=From, body=Body))
    return reply.text
