# Clean-room Reverse Engineering: SmartPromptIQ-style Agentic Business OS

## Scope

This document records **publicly observable** product concepts and independently derived implementation requirements. No private source, credentials, hidden endpoints, copyrighted assets, or non-public access were used.

## Public source URLs reviewed

- https://www.smartpromptiq-staff.com/
- https://smartpromptiqaistaff.com/
- https://smartpromptiqaistaff.com/about/how-it-work/
- https://smartpromptiqaistaff.com/meet-the-team/
- https://smartpromptiqaistaff.com/command-center/
- https://smartpromptiqaistaff.com/pricing-2/
- https://smartpromptiqaistaff.com/live-demo/

Reviewed September 2026.

## Product thesis

The product is positioned as an **agentic AI business operating system**, not a prompt generator. Its public experience combines:

1. Named specialist AI staff.
2. A shared workspace-level business profile / knowledge base ("Business Brain").
3. Manager-led delegation into specialist subtasks.
4. Scheduled, event, manual, and webhook-triggered workflows.
5. Real-world actions through a separate execution/integration layer.
6. Human approval and action guardrails.
7. Command Center observability for agents, workflows, delegations, usage, cost, and health.
8. Voice, chat, SMS, marketplace, billing, and multi-company capabilities.

## Publicly stated onboarding lifecycle

1. User signs up and a workspace/free plan is provisioned.
2. Two starter staff members are seeded (Operations + Research).
3. User fills a shared Business Profile and Knowledge Base.
4. Agents receive direct work and scheduled workflows begin running.
5. Higher tiers enable voice/chat and autonomous external actions.

## Publicly stated implementation signals

The product's own public documentation names:

- PostgreSQL + Prisma for persistence.
- Anthropic Claude for reasoning.
- OpenClaw as the external-action execution layer.
- OAuth and webhooks for integrations.
- Twilio Voice for telephony.
- Stripe + Stripe Connect for subscription billing and marketplace payouts.
- TOTP-based 2FA, encrypted secrets, workspace isolation, backups, and audit logs.

These are vendor claims, not an independent infrastructure audit.

## Core product primitives derived from behavior

### Workspace
Tenant boundary containing subscription, agents, knowledge, integrations, workflows, and usage.

### Agent template
Reusable role definition: objective, instructions, tools, defaults, personality ranges, manager capability.

### Agent instance
Workspace deployment of a template with customized model, personality, memory scope, autonomy, budget, and permissions.

### Business Brain
Shared structured company facts + documents + SOPs + rules + brand voice + version history.

### Delegation
A goal decomposed by a manager into an explicit task graph with dependencies and specialist assignments.

### Workflow
Versioned graph of nodes and edges plus trigger definitions. A run references an immutable workflow version.

### Tool gateway
Centralized integration execution. Agents request normalized tools; policy checks decide whether calls are allowed, denied, or require approval.

### Approval
Human checkpoint for sensitive side effects such as bulk messaging, refunds, production changes, or destructive actions.

### Command Center
Operational read model combining agent states, workflow health, task throughput, approvals, costs, and alerting.

## Important product observations

- Public demo pages identify some dashboards as simulations. Therefore animated numbers are treated as UX references, not proof of runtime execution.
- Public pages have used both 24+ and 25 for staff counts; counts should be modeled as catalog data rather than hard-coded product logic.
- Public pricing/feature pages evolve; entitlements should be data-driven.
- Marketing language around "self-healing" should be implemented narrowly: retries, credential refresh, provider fallback, circuit breakers, and escalation.

## Clean-room differentiation

This implementation intentionally improves the architecture with:

- Multi-model provider abstraction.
- Explicit task DAGs.
- Durable state machines.
- Reversible-action metadata.
- Fine-grained autonomy levels.
- Central policy enforcement.
- Per-agent budgets.
- Full audit events.
- Provider-neutral connector interface.
- Production-friendly evaluation hooks.
