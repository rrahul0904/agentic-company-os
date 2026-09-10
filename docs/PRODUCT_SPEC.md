# Product Specification

## Product name

Agentic Company OS

## Positioning

**Build, deploy, and govern an AI workforce across your company.**

## Personas

- Solo founder
- Small business operator
- Agency / multi-client operator
- Functional team leader
- Enterprise operations / automation team

## Autonomy modes

### Assist
Read data and draft recommendations. No external side effects.

### Supervised
External side effects are proposed but require human approval.

### Autonomous
Only pre-authorized actions may execute automatically, bounded by scopes, budgets, rate limits, and policy.

## MVP journeys

### 1. Onboard a company
Create workspace → fill Business Brain → select agent team → connect tools → view Command Center.

### 2. Ask a specialist
Open agent → submit goal → retrieve Business Brain context → model generation → persist result + usage + audit.

### 3. Delegate a goal
Submit goal to manager → planner creates task DAG → specialists execute ready tasks → manager synthesizes → approval if needed → result delivered.

### 4. Build a workflow
Choose trigger → add agent/tool/condition/approval nodes → save immutable version → activate → inspect runs and failures.

### 5. Approve a sensitive action
Agent proposes side effect → policy emits REQUIRE_APPROVAL → approval queue → user approves/rejects → action executes or cancels → audit event records outcome.

## Command Center

Required panels:

- Active agents
- Running workflows
- Delegations
- Tasks completed
- Success rate
- Token and cost usage
- Approval backlog
- Alerts
- Recent audit events
- Per-agent performance

## Business Brain

Structured fields:

- company profile
- products/services
- pricing
- target customers
- competitors
- brand voice
- goals
- do rules
- don't rules
- SOPs
- FAQs
- uploaded knowledge

Knowledge entries are versioned and scoped.

## Agent catalog

Initial independent catalog:

- Operations Lead
- Research Analyst
- Content Strategist
- Social Manager
- Email Marketer
- Sales Specialist
- SEO Analyst
- Finance Analyst
- Customer Support
- Technical Writer
- Engineering Assistant
- Brand Strategist

Agents share infrastructure. They differ by role instructions, knowledge scope, tools, output schemas, workflow defaults, and permissions.

## Non-functional requirements

- Tenant isolation
- Idempotent tool execution
- Durable workflow/task status
- Auditability
- Retries with backoff
- Rate limiting
- Cost budgets
- Secret encryption
- RBAC
- Observability
- Export/delete tenant data
- Provider failover
