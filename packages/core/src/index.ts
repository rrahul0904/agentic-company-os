export type AutonomyLevel = "ASSIST" | "SUPERVISED" | "AUTONOMOUS";
export type RunStatus = "CREATED"|"QUEUED"|"PLANNING"|"RUNNING"|"WAITING_TOOL"|"WAITING_APPROVAL"|"RETRY_WAIT"|"SUCCEEDED"|"FAILED"|"REJECTED"|"DEAD_LETTER"|"CANCELLED";
export type ToolRisk = "READ"|"DRAFT"|"REVERSIBLE_WRITE"|"EXTERNAL_WRITE"|"SENSITIVE"|"DESTRUCTIVE";
export interface BusinessContext { workspaceId:string; facts:Record<string,string>; rules:{dos:string[];donts:string[]}; documents:Array<{id:string;title:string;excerpt:string}> }
export interface AgentDefinition { id:string; name:string; role:string; department:string; objective:string; manager:boolean; tools:string[]; autonomy:AutonomyLevel; monthlyBudgetUsd:number }
export interface PlannedTask { id:string; title:string; assignedAgentId:string; dependsOn:string[]; requestedAction?:string }
export interface DelegationPlan { goal:string; managerAgentId:string; tasks:PlannedTask[] }
export interface PolicyInput { autonomy:AutonomyLevel; tool:string; action:string; risk:ToolRisk; amountUsd?:number; recipientCount?:number; environment?:"dev"|"staging"|"production" }
export type PolicyDecision = {decision:"ALLOW"|"DENY"|"REQUIRE_APPROVAL"; reason:string};
