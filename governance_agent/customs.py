from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from .models import IntentProposal, OperationKind, RiskLevel, TriageDecision


class TriageGate:
    HIGH_RISK_ACTIONS = {
        "delete_records",
        "financial_transfer",
        "send_bulk_email",
        "erp_stock_transfer",
    }

    def evaluate(self, proposal: IntentProposal) -> TriageDecision:
        if proposal.operation == OperationKind.READ:
            return TriageDecision(
                risk=RiskLevel.LOW,
                requires_hitl=False,
                reason="Read-only operations are in the autonomous zone.",
            )
        if proposal.action_type in self.HIGH_RISK_ACTIONS:
            return TriageDecision(
                risk=RiskLevel.HIGH,
                requires_hitl=True,
                reason="High-risk mutation requires explicit human approval.",
            )
        return TriageDecision(
            risk=RiskLevel.MEDIUM,
            requires_hitl=True,
            reason="Mutations use the assisted or HITL zone.",
        )


class ActionParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str | None = None
    recipient: str | None = None
    amount_cents: int | None = None
    dry_run: bool = False


class InspectionGate:
    def inspect(self, proposal: IntentProposal) -> ActionParameters:
        return ActionParameters.model_validate(proposal.parameters)


class DryRunResult(BaseModel):
    valid: bool
    conflicts: list[str] = []


class DryRunGate(ABC):
    @abstractmethod
    def execute(self, action_type: str, parameters: dict[str, Any]) -> DryRunResult:
        """Simulate an action without changing external systems."""


class InMemoryDryRunGate(DryRunGate):
    def execute(self, action_type: str, parameters: dict[str, Any]) -> DryRunResult:
        if action_type == "delete_records" and not parameters.get("record_id"):
            return DryRunResult(valid=False, conflicts=["record_id is required"])
        if action_type == "financial_transfer" and not parameters.get("amount_cents"):
            return DryRunResult(valid=False, conflicts=["amount_cents is required"])
        return DryRunResult(valid=True)
