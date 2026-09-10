# Architecture

## Control plane vs execution plane

```text
CONTROL PLANE
Users → Workspace → Agents → Delegations → Workflows → Policies → Approvals
                                     │
                                     ▼
EXECUTION PLANE
Queue/Worker → LLM Router → Tool Gateway → Connectors → External Systems
     │              │            │
     └──────────── Audit / Usage / Events ────────────┘
                                     │
                                     ▼
                              Command Center
```

## Recommended production stack

- Web/API: Next.js App Router + TypeScript
- Database: PostgreSQL + Prisma
- Retrieval: pgvector
- Queue/durability: Temporal, Trigger.dev, or another durable execution runtime
- Cache/ephemeral locks: Redis where needed
- Model layer: provider-neutral adapter; OpenAI/Anthropic/Gemini supported
- Auth: OIDC provider + workspace RBAC
- Billing: Stripe
- Voice/SMS: Twilio-compatible connector
- Observability: OpenTelemetry + error monitoring + LLM traces
- Secrets: KMS/Vault-backed encryption envelope

## Agent runtime

Every run follows a durable lifecycle:

```text
CREATED → QUEUED → PLANNING → RUNNING → WAITING_TOOL → RUNNING
                                    └→ WAITING_APPROVAL → RUNNING
RUNNING → SUCCEEDED
RUNNING → FAILED → RETRY_WAIT → QUEUED
RUNNING → DEAD_LETTER
```

## Delegation DAG

A manager produces structured tasks rather than spawning uncontrolled recursive agents.

```text
Goal
 ├─ Research ─────────────┐
 ├─ Content ← Research    ├─ Brand Review → Finalize
 └─ Distribution ← Finalize
```

Task readiness is computed from dependency completion.

## Tool security

Agents never handle provider secrets directly.

```text
Agent request
  ↓
Normalized tool call
  ↓
Policy engine
  ├─ allow
  ├─ deny
  └─ require approval
  ↓
Connector executor
  ↓
Idempotency + audit + result
```

## Policy dimensions

- Workspace role
- Agent role
- Autonomy level
- Tool/action
- Resource scope
- Side-effect severity
- Reversibility
- Monetary value
- Recipient count
- Environment (dev/staging/prod)
- Daily/weekly budget

## Self-healing definition

Supported:

- exponential retry
- OAuth refresh
- provider fallback
- malformed structured-output repair
- circuit breakers
- stale-run detection
- operator escalation

Not supported by default:

- unrestricted self-modification
- silent privilege expansion
- arbitrary infrastructure mutation
