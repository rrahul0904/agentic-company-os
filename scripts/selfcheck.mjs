import { readFileSync, existsSync } from 'node:fs';
const required=['README.md','docs/REVERSE_ENGINEERING.md','docs/ARCHITECTURE.md','prototype/server.py','prototype/static/index.html','prisma/schema.prisma','packages/policy-engine/src/index.ts','apps/web/src/app/page.tsx'];
let bad=0;for(const p of required){if(!existsSync(new URL('../'+p,import.meta.url))){console.error('missing',p);bad++}}
const schema=readFileSync(new URL('../prisma/schema.prisma',import.meta.url),'utf8');for(const model of ['Workspace','AgentInstance','Delegation','Workflow','ApprovalRequest','AuditEvent']){if(!schema.includes('model '+model)){console.error('missing model',model);bad++}}
if(bad)process.exit(1);console.log(`selfcheck passed: ${required.length} required files + core Prisma models`);
