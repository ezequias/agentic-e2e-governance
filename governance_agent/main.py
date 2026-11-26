from governance_agent.actions import InMemoryActionExecutor
from governance_agent.customs import InMemoryDryRunGate
from governance_agent.intent import StaticIntentGenerator
from governance_agent.pipeline import GovernedPipeline, HumanApprovalRequired
from governance_agent.state import InMemoryStateReader, InMemoryStateStore


def main() -> None:
    proposal = {
        "intent": "Review a customer record",
        "operation": "read",
        "action_type": "get_customer",
        "parameters": {"record_id": "customer-42"},
    }
    pipeline = GovernedPipeline(
        state_reader=InMemoryStateReader({"proposal": proposal}),
        state_store=InMemoryStateStore(),
        intent_generator=StaticIntentGenerator(),
        action_executor=InMemoryActionExecutor(),
        dry_run_gate=InMemoryDryRunGate(),
    )
    print(pipeline.submit("Show the customer record"))

    risky_proposal = {
        "intent": "Transfer stock",
        "operation": "mutate",
        "action_type": "erp_stock_transfer",
        "parameters": {"record_id": "stock-42"},
    }
    risky_pipeline = GovernedPipeline(
        state_reader=InMemoryStateReader({"proposal": risky_proposal}),
        state_store=InMemoryStateStore(),
        intent_generator=StaticIntentGenerator(),
        action_executor=InMemoryActionExecutor(),
        dry_run_gate=InMemoryDryRunGate(),
    )
    try:
        risky_pipeline.submit("Transfer stock")
    except HumanApprovalRequired as exc:
        print({
            "status": exc.gate.status,
            "trace_id": exc.trace_id,
            "message": str(exc),
        })


if __name__ == "__main__":
    main()
