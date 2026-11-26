from abc import ABC, abstractmethod
from typing import Any


class StateReader(ABC):
    @abstractmethod
    def read(self, trace_id: str) -> dict[str, Any]:
        """Read factual context needed to construct an intent."""


class StateStore(ABC):
    @abstractmethod
    def append(self, trace_id: str, event: dict[str, Any]) -> None:
        """Persist an immutable state or audit event."""


class InMemoryStateReader(StateReader):
    def __init__(self, context: dict[str, Any] | None = None) -> None:
        self.context = context or {}

    def read(self, trace_id: str) -> dict[str, Any]:
        return {"trace_id": trace_id, **self.context}


class InMemoryStateStore(StateStore):
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def append(self, trace_id: str, event: dict[str, Any]) -> None:
        self.events.append({"trace_id": trace_id, **event})
