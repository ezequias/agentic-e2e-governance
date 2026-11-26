from abc import ABC, abstractmethod
from typing import Any


class ActionExecutor(ABC):
    @abstractmethod
    def execute(self, action_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute a prevalidated, authorized action."""


class InMemoryActionExecutor(ActionExecutor):
    def execute(self, action_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if parameters.get("dry_run"):
            return {"status": "dry_run", "action_type": action_type}
        return {"status": "executed", "action_type": action_type, "parameters": parameters}
