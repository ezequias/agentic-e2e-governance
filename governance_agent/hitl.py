from enum import Enum

from pydantic import BaseModel, Field


class HumanDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


class HumanGate(BaseModel):
    status: str = "pending"
    operator_id: str | None = None
    decision: HumanDecision | None = None

    def resolve(self, operator_id: str, decision: HumanDecision) -> None:
        if self.status != "pending":
            raise RuntimeError("Human gate has already been resolved")
        self.operator_id = operator_id
        self.decision = decision
        self.status = "approved" if decision == HumanDecision.APPROVE else "rejected"
