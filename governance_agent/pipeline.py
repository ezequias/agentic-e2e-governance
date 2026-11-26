from typing import Any

from pydantic import ValidationError

from .actions import ActionExecutor
from .customs import DryRunGate, InspectionGate, TriageGate
from .hitl import HumanGate
from .intent import IntentGenerator
from .models import IntentProposal
from .state import StateReader, StateStore


class PipelineRejected(Exception):
    pass


class HumanApprovalRequired(PipelineRejected):
    def __init__(self, trace_id: str, gate: HumanGate) -> None:
        super().__init__("Action requires durable human approval")
        self.trace_id = trace_id
        self.gate = gate


class GovernedPipeline:
    def __init__(
        self,
        state_reader: StateReader,
        state_store: StateStore,
        intent_generator: IntentGenerator,
        action_executor: ActionExecutor,
        dry_run_gate: DryRunGate,
    ) -> None:
        self.state_reader = state_reader
        self.state_store = state_store
        self.intent_generator = intent_generator
        self.action_executor = action_executor
        self.dry_run_gate = dry_run_gate
        self.triage_gate = TriageGate()
        self.inspection_gate = InspectionGate()

    def submit(self, objective: str) -> dict[str, Any]:
        probe = IntentProposal(
            intent="trace-context",
            operation="read",
            action_type="trace_context",
        )
        context = self.state_reader.read(str(probe.trace_id))

        proposal = self.intent_generator.generate(objective, context)
        triage = self.triage_gate.evaluate(proposal)
        self.state_store.append(str(proposal.trace_id), {
            "stage": "triage",
            "outcome": triage.risk.value,
            "details": triage.model_dump(),
        })

        try:
            parameters = self.inspection_gate.inspect(proposal)
        except ValidationError as exc:
            raise PipelineRejected(f"Intent inspection failed: {exc}") from exc

        dry_run = self.dry_run_gate.execute(
            proposal.action_type,
            parameters.model_dump(exclude_none=True),
        )
        self.state_store.append(str(proposal.trace_id), {
            "stage": "dry_run",
            "outcome": "valid" if dry_run.valid else "invalid",
            "details": dry_run.model_dump(),
        })
        if not dry_run.valid:
            raise PipelineRejected(f"Dry-run failed: {dry_run.conflicts}")

        if triage.requires_hitl:
            gate = HumanGate(status="pending")
            self.state_store.append(str(proposal.trace_id), {
                "stage": "hitl",
                "outcome": "pending",
                "details": {"action_type": proposal.action_type},
            })
            raise HumanApprovalRequired(str(proposal.trace_id), gate)

        result = self.action_executor.execute(
            proposal.action_type,
            parameters.model_dump(exclude_none=True),
        )
        self.state_store.append(str(proposal.trace_id), {
            "stage": "action",
            "outcome": "executed",
            "details": result,
        })
        return result
