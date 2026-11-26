from governance_agent.actions import InMemoryActionExecutor
from governance_agent.customs import InMemoryDryRunGate
from governance_agent.intent import StaticIntentGenerator
from governance_agent.pipeline import GovernedPipeline, HumanApprovalRequired
from governance_agent.state import InMemoryStateReader, InMemoryStateStore


def build_pipeline(proposal):
    return GovernedPipeline(
        state_reader=InMemoryStateReader({"proposal": proposal}),
        state_store=InMemoryStateStore(),
        intent_generator=StaticIntentGenerator(),
        action_executor=InMemoryActionExecutor(),
        dry_run_gate=InMemoryDryRunGate(),
    )


def test_read_action_executes_without_hitl():
    pipeline = build_pipeline({
        "intent": "Read a customer",
        "operation": "read",
        "action_type": "get_customer",
        "parameters": {"record_id": "customer-1"},
    })

    result = pipeline.submit("Show customer")

    assert result["status"] == "executed"


def test_mutation_requires_hitl():
    pipeline = build_pipeline({
        "intent": "Transfer stock",
        "operation": "mutate",
        "action_type": "erp_stock_transfer",
        "parameters": {"record_id": "stock-1"},
    })

    try:
        pipeline.submit("Transfer stock")
        assert False, "Expected human approval requirement"
    except HumanApprovalRequired as exc:
        assert exc.gate.status == "pending"
