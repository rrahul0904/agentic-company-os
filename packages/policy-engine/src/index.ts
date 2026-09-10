import type { PolicyDecision, PolicyInput } from "@agentic/core";
export function evaluatePolicy(input:PolicyInput):PolicyDecision {
  if(input.risk==="DESTRUCTIVE") return {decision:"REQUIRE_APPROVAL",reason:"Destructive actions always require explicit approval"};
  if(input.environment==="production" && input.risk!=="READ") return {decision:"REQUIRE_APPROVAL",reason:"Production writes require approval"};
  if((input.amountUsd??0)>0) return {decision:"REQUIRE_APPROVAL",reason:"Monetary actions require approval"};
  if((input.recipientCount??0)>20) return {decision:"REQUIRE_APPROVAL",reason:"Bulk external communication requires approval"};
  if(input.autonomy==="ASSIST" && !["READ","DRAFT"].includes(input.risk)) return {decision:"DENY",reason:"Assist mode cannot perform side effects"};
  if(input.autonomy==="SUPERVISED" && ["EXTERNAL_WRITE","SENSITIVE"].includes(input.risk)) return {decision:"REQUIRE_APPROVAL",reason:"Supervised mode requires approval for external/sensitive writes"};
  return {decision:"ALLOW",reason:"Action fits configured autonomy and policy"};
}
