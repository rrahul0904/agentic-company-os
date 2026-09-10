# Implementation Plan

## Phase 0 — reverse engineering and foundations

- [x] Public product feature decomposition
- [x] Clean-room boundary documented
- [x] Working local prototype
- [x] Production domain schema
- [x] Agent runtime state machine
- [x] Policy model
- [x] Tool gateway contract
- [x] Command Center shell

## Phase 1 — production vertical slice

- [ ] Install dependencies and lockfile
- [ ] PostgreSQL migrations
- [ ] Authentication + organizations + memberships
- [ ] CRUD: Business Brain
- [ ] CRUD: agent instances
- [ ] LLM provider adapter + mock provider
- [ ] Direct agent chat with persistent runs
- [ ] Usage/cost accounting
- [ ] Audit event viewer

## Phase 2 — delegation

- [ ] Manager planner structured output
- [ ] Task DAG validation
- [ ] Ready-task scheduler
- [ ] Specialist execution
- [ ] Synthesis task
- [ ] Retry/dead-letter handling
- [ ] Delegation visualization

## Phase 3 — workflows

- [ ] Versioned workflow builder
- [ ] Manual triggers
- [ ] Cron triggers
- [ ] Webhook triggers
- [ ] Conditions
- [ ] Delay
- [ ] Tool/action nodes
- [ ] Approval nodes
- [ ] Execution logs

## Phase 4 — connectors and autonomy

- [ ] OAuth connection service
- [ ] Gmail/Outlook
- [ ] Slack
- [ ] GitHub
- [ ] Stripe
- [ ] HubSpot
- [ ] Shopify
- [ ] Twilio
- [ ] Custom HTTP/MCP
- [ ] Policy templates
- [ ] Autonomous bounded execution

## Phase 5 — commercial surface

- [ ] Stripe subscriptions
- [ ] Entitlements
- [ ] Usage caps
- [ ] Marketplace
- [ ] Creator payouts
- [ ] Multi-company dashboard
- [ ] White-label settings
- [ ] SSO/RBAC hardening

## Release gate

Do not call the project production complete until:

- all migrations are reproducible
- all integration writes have idempotency keys
- all sensitive actions have policy coverage
- tests cover state transitions and tenant isolation
- external connector contracts are integration-tested
- audit records are immutable
- secrets are encrypted with production key management
- browser E2E passes for core journeys
- load and failure-mode testing complete
