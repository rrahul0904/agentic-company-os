export type WorkflowNodeType="AGENT"|"TOOL"|"CONDITION"|"DELAY"|"APPROVAL"|"TRANSFORM"|"NOTIFY";
export interface WorkflowNode { id:string; type:WorkflowNodeType; config:Record<string,unknown> }
export interface WorkflowEdge { from:string; to:string; when?:"always"|"true"|"false" }
export interface WorkflowDefinition { version:number; trigger:{type:"MANUAL"|"SCHEDULED"|"EVENT"|"WEBHOOK";config:Record<string,unknown>}; nodes:WorkflowNode[]; edges:WorkflowEdge[] }
export function validateWorkflow(w:WorkflowDefinition){
 const ids=new Set(w.nodes.map(n=>n.id)); if(ids.size!==w.nodes.length) throw new Error("Duplicate workflow node id");
 for(const e of w.edges) if(!ids.has(e.from)||!ids.has(e.to)) throw new Error(`Invalid edge ${e.from} -> ${e.to}`);
 return true;
}
