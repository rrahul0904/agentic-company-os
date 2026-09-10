import type { RunStatus } from "@agentic/core";
const transitions: Record<RunStatus, RunStatus[]> = {
 CREATED:["QUEUED","CANCELLED"], QUEUED:["PLANNING","RUNNING","CANCELLED"], PLANNING:["RUNNING","FAILED","CANCELLED"],
 RUNNING:["WAITING_TOOL","WAITING_APPROVAL","SUCCEEDED","FAILED","CANCELLED"], WAITING_TOOL:["RUNNING","FAILED","CANCELLED"],
 WAITING_APPROVAL:["RUNNING","REJECTED","CANCELLED"], RETRY_WAIT:["QUEUED","DEAD_LETTER","CANCELLED"], SUCCEEDED:[],
 FAILED:["RETRY_WAIT","DEAD_LETTER"], REJECTED:[], DEAD_LETTER:[], CANCELLED:[]
};
export function canTransition(from:RunStatus,to:RunStatus){ return transitions[from].includes(to); }
export function assertTransition(from:RunStatus,to:RunStatus){ if(!canTransition(from,to)) throw new Error(`Invalid run transition ${from} -> ${to}`); }
export function readyTaskIds(tasks:Array<{id:string;status:RunStatus;dependsOn:string[]}>){ const done=new Set(tasks.filter(t=>t.status==="SUCCEEDED").map(t=>t.id)); return tasks.filter(t=>t.status==="QUEUED"&&t.dependsOn.every(d=>done.has(d))).map(t=>t.id); }
