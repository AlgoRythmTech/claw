from dataclasses import dataclass
from enum import Enum


class ContactTier(str, Enum):
    master = "master"
    close = "close"
    professional = "professional"
    high_priority = "high_priority"
    unknown = "unknown"


@dataclass(slots=True)
class IncomingMessage:
    sender: str
    body: str


@dataclass(slots=True)
class SecretaryReply:
    text: str
    action_taken: str | None = None
