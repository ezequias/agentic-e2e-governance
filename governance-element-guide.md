# E2E Agentic Governance Overview

This guide explains the layers, gates, and transitions in the [animated architecture diagram](./.archify/architecture-it-governance-20261126-1155/e2e-agentic-it-operations.html).

## Layer 1: State

The State layer is the factual context source for an agent run. It can include a data warehouse, relational records, vector search for retrieval-augmented generation (RAG), and event history. The intent generator reads this context; it does not receive direct write access to these stores.

## Layer 2: Intent - LLM

The language model interprets the request and available context, then proposes an action as structured JSON. Treat that proposal as untrusted input: the model suggests what should happen, but cannot execute tools or mutate business data itself.

## Layer 3: Deterministic Customs / Quarantine

The customs boundary contains three sequential gates. A proposal must pass each gate before an action can reach the execution layer.

### 3.1 Triage

Triage classifies the operation's blast radius and whether it is read-only or mutating. Read-only, low-risk work can follow the autonomous path. Mutations are assessed for risk and routed through the required controls; high-risk work must not run with high autonomy.

### 3.2 Inspect

Inspection validates the proposal's schema and types, sanitizes inputs, and supplies trusted execution dependencies such as credentials and context. A malformed proposal is rejected or returned for correction; it does not proceed to execution.

### 3.3 Test + HITL

The system dry-runs an action before execution. Medium- and high-risk actions pause at a durable Human-in-the-Loop (HITL) gate so an authorized operator can approve or reject the exact parameters. Rejection or a failed dry-run prevents execution.

## Layer 4: Action

Typed connectors and Model Context Protocol (MCP) servers perform deterministic tool calls to APIs, ERPs, or messaging systems. They receive only validated and authorized payloads; the LLM is not the executor.

## Arrows and feedback loop

1. **Context injection / state read** - factual state is supplied to the reasoning layer.
2. **Untrusted intent proposal** - the LLM submits structured intent to the quarantine boundary.
3. **Authorized payload** - after triage, inspection, dry-run, and any required human approval, the action layer may execute.
4. **State update / immutable event** - the result and audit event are persisted back into state, so later runs can use the updated source of truth.

The dashed return arrow represents state and audit feedback; it is not a direct path for the LLM to write to the data store.

## Motion and reading the diagram

Use the **Live / Still** control in the diagram viewer to turn the animated flow on or off. Motion illustrates the direction of the process; it does not represent measured timing or execution status.
