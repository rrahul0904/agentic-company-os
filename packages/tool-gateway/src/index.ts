import type { AutonomyLevel, ToolRisk } from "@agentic/core";
import { evaluatePolicy } from "@agentic/policy-engine";
export interface ToolRequest { workspaceId:string; agentId:string; tool:string; action:string; input:unknown; autonomy:AutonomyLevel; risk:ToolRisk; idempotencyKey:string; }
export interface Connector { name:string; execute(action:string,input:unknown,ctx:{workspaceId:string;idempotencyKey:string}):Promise<unknown> }
export class ToolGateway {
  constructor(private connectors:Map<string,Connector>){}
  async request(r:ToolRequest){
    const policy=evaluatePolicy({autonomy:r.autonomy,tool:r.tool,action:r.action,risk:r.risk});
    if(policy.decision!=="ALLOW") return {status:policy.decision,reason:policy.reason};
    const connector=this.connectors.get(r.tool); if(!connector) throw new Error(`Unknown connector: ${r.tool}`);
    const output=await connector.execute(r.action,r.input,{workspaceId:r.workspaceId,idempotencyKey:r.idempotencyKey});
    return {status:"SUCCEEDED",output};
  }
}
