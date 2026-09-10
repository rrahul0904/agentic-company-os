export interface ModelRequest { system:string; prompt:string; jsonSchema?:Record<string,unknown>; maxOutputTokens?:number }
export interface ModelResult { text:string; usage:{inputTokens:number;outputTokens:number}; model:string; provider:string }
export interface ModelProvider { generate(req:ModelRequest):Promise<ModelResult> }
export class MockModelProvider implements ModelProvider {
 async generate(req:ModelRequest):Promise<ModelResult>{ const text=`Mock agent result for: ${req.prompt}`; return {text,usage:{inputTokens:Math.ceil(req.prompt.length/4),outputTokens:Math.ceil(text.length/4)},model:"mock-v1",provider:"mock"}; }
}
