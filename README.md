# Agentic E2E Governance

This repository contains a runnable implementation skeleton for the architecture described in `specification.md`.

The skeleton enforces the core separation:

1. `StateReader` supplies factual context.
2. `IntentGenerator` produces an untrusted intent proposal.
3. The deterministic customs pipeline performs triage, schema inspection, dry-run testing, and HITL gating.
4. `ActionExecutor` performs mutations only after the proposal is authorized.
5. `StateStore` records the resulting immutable event.

This is a reference implementation, not a deployment-ready integration. External providers for LLM inference, Temporal, MCP, PostgreSQL, OTel, and ClickHouse are represented through interfaces and will require adapter implementations.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
python -m governance_agent.main
```
