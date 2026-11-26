from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class OperationKind(str, Enum):
    READ = "read"
    MUTATE = "mutate"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class IntentProposal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    trace_id: UUID = Field(default_factory=uuid4)
    intent: str = Field(min_length=1, max_length=500)
    operation: OperationKind
    action_type: str = Field(min_length=1, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)


class TriageDecision(BaseModel):
    risk: RiskLevel
    requires_hitl: bool
    reason: str


class AuditEvent(BaseModel):
    trace_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stage: str
    outcome: str
    details: dict[str, Any] = Field(default_factory=dict)
