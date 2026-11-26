# How Does Agentic IT Operations Stay Governed? {#agentic-operations}

Safe agent operations keep the LLM on the proposal side and place deterministic governance gates between every proposal and execution.

- The agent receives factual state as context but does not write to it directly.
- Triage, schema inspection, dry-run, and human approval control the proposed action.
- Typed connectors execute authorized actions and return results to the audit and state loop.

@answer scope="Conceptual workflow based on the supplied architecture; exact risk thresholds and integrations are implementation-specific."
@meta locale=en

## How does a request cross the governance boundary? {#governed-flow}

@diagram workflow source=flow.json title="Agentic IT Operations Governance Flow"

## What happens at each control point? {#control-points}

| Condition | Governance response | Execution result |
| --- | --- | --- |
| Read-only, low-risk request | Triage classifies the request as read-only. | It may use the autonomous path without a data mutation. |
| Proposed mutation | Inspect validates the schema and sanitizes parameters; the system dry-runs the action. | The proposal proceeds only if validation and simulation pass. |
| Medium- or high-risk action | Pause at a durable Human-in-the-Loop gate for an operator's decision. | Execute only after audited approval; rejection blocks the action. |
| Invalid proposal or failed dry-run | Reject it or return a validation error for correction. | No action is executed from the failed proposal. |
| Completed action | Correlate the outcome with its trace and persist an immutable event or checkpoint. | Later requests read the refreshed state. |

@callout id=governance-invariant level=warning title="The LLM never executes"
The model creates an untrusted proposal. Only deterministic, typed action code receives a validated and authorized payload.
