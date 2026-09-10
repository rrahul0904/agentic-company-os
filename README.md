# Agentic Company OS

A clean-room implementation inspired by public patterns in agentic business operating systems: shared business context, specialized AI workers, manager delegation, durable workflows, governed external actions, approvals, and real-time operational visibility.

> This repository does **not** contain SmartPromptIQ proprietary source code, private APIs, branding, assets, or copied implementation. The reverse-engineering notes are based only on publicly observable product behavior and published product documentation.

## What is already implemented

- Dependency-free runnable prototype backed by SQLite
- Workspace + Business Brain
- Seeded specialist agent registry
- Delegation planner with task DAGs
- Policy engine that routes sensitive actions to human approval
- Workflow definitions and scheduled/manual trigger metadata
- Audit/event stream
- Usage/cost model
- Command Center UI
- Production-oriented Next.js/TypeScript monorepo scaffold
- Prisma/PostgreSQL production schema
- Core domain types and runtime state machine
- Self-check and unit tests

## Run the working prototype

```bash
cd prototype
python3 server.py
```

Open `http://127.0.0.1:8080`.

Run tests:

```bash
python3 -m unittest discover -s prototype/tests -v
```

## Production architecture

```text
Web / API
   │
   ├── Identity + Workspaces
   ├── Business Brain / Retrieval
   ├── Agent Control Plane
   ├── Delegation Engine
   ├── Workflow Engine
   ├── Policy + Approval Engine
   ├── Tool Gateway
   └── Command Center / Audit
              │
        PostgreSQL + pgvector
              │
       Durable Worker Runtime
              │
      Model + Connector Adapters
```

See:

- `docs/REVERSE_ENGINEERING.md`
- `docs/PRODUCT_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/FEATURE_MATRIX.md`
- `docs/IMPLEMENTATION_PLAN.md`

## Principles

1. Agents never receive vendor credentials directly.
2. Every external side effect passes through a policy-controlled tool gateway.
3. Sensitive actions require explicit approval by default.
4. Every model/tool/action invocation is auditable.
5. Delegations are explicit DAGs rather than uncontrolled recursive agent spawning.
6. Autonomous mode means pre-authorized bounded actions, not unrestricted access.
7. Provider adapters are replaceable; the product is not locked to one model vendor.

## License

MIT for this independent implementation. Third-party services remain subject to their own licenses and terms.
