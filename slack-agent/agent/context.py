"""Per-request context that tools can read (who asked, from where)."""

from contextvars import ContextVar
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RequestContext:
    user_id: str
    user_name: str
    channel_id: str
    thread_ts: str = None
    # Text that tools want posted verbatim after Claude's reply (e.g. tables), so the model can't alter it.
    attachments: list = field(default_factory=list)


current_request: ContextVar[RequestContext] = ContextVar("current_request")
