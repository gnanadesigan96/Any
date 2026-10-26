"""Per-request context that tools can read (who asked, from where)."""

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestContext:
    user_id: str
    user_name: str
    channel_id: str


current_request: ContextVar[RequestContext] = ContextVar("current_request")
