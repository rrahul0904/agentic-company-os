const agents=[{id:"ops",name:"Nova",role:"Operations Lead",manager:true},{id:"research",name:"Atlas",role:"Research Analyst",manager:false}];
export async function GET(){return Response.json({agents})}
