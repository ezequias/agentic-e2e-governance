from abc import ABC, abstractmethod

from .models import IntentProposal


class IntentGenerator(ABC):
    @abstractmethod
    def generate(self, objective: str, context: dict) -> IntentProposal:
        """Generate an untrusted intent proposal."""


class StaticIntentGenerator(IntentGenerator):
    """Deterministic adapter for examples and tests."""

    def generate(self, objective: str, context: dict) -> IntentProposal:
        if context.get("proposal"):
            return IntentProposal.model_validate(context["proposal"])
        raise ValueError("No intent proposal supplied")
