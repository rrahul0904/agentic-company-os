from __future__ import annotations
import json, uuid, re
from datetime import datetime, timezone
from db import emit, now

SENSITIVE_PATTERNS = {
    "BULK_MESSAGE": re.compile(r"\b(send|email|message|dm)\b.*\b(all|bulk|campaign|customers|leads)\b", re.I),
    "MONEY": re.compile(r"\b(refund|charge|pay|payment|invoice|purchase|spend|transfer)\b", re.I),
    "DESTRUCTIVE": re.compile(r"\b(delete|drop|destroy|terminate|remove production)\b", re.I),
    "PRODUCTION": re.compile(r"\b(deploy|modify|change|restart)\b.*\b(prod|production)\b", re.I),
}

def id_(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

def policy_decision(action: str, autonomy: str = "SUPERVISED"):
    reasons = [name for name, pattern in SENSITIVE_PATTERNS.items() if pattern.search(action or "")]
    if reasons:
        return {"decision": "REQUIRE_APPROVAL", "reason": ", ".join(reasons)}
    if autonomy == "ASSIST":
        return {"decision": "DENY_SIDE_EFFECT", "reason": "Assist mode is read/draft only"}
    return {"decision": "ALLOW", "reason": "Action is within current policy"}

def choose_agent(title: str):
    t = title.lower()
    if any(k in t for k in ["research", "competitor", "market"]): return "agent_research"
    if any(k in t for k in ["write", "content", "blog", "email copy"]): return "agent_content"
    if any(k in t for k in ["lead", "sales", "pipeline"]): return "agent_sales"
    if any(k in t for k in ["finance", "revenue", "budget"]): return "agent_finance"
    if any(k in t for k in ["support", "ticket", "faq"]): return "agent_support"
    if any(k in t for k in ["code", "deploy", "technical", "security"]): return "agent_engineer"
    if any(k in t for k in ["brand", "voice", "positioning"]): return "agent_brand"
    return "agent_ops"

def plan_goal(goal: str):
    g = goal.strip()
    lower = g.lower()
    tasks = []
    if any(k in lower for k in ["campaign", "launch", "market"]):
        tasks = [
          {"title": "Research market and audience", "agent": "agent_research", "depends": []},
          {"title": "Draft campaign content", "agent": "agent_content", "depends": [0]},
          {"title": "Review brand consistency", "agent": "agent_brand", "depends": [1]},
          {"title": "Prepare distribution plan", "agent": "agent_ops", "depends": [2]},
        ]
    elif any(k in lower for k in ["incident", "security", "production", "bug"]):
        tasks = [
          {"title": "Collect technical evidence", "agent": "agent_engineer", "depends": []},
          {"title": "Assess operational impact", "agent": "agent_ops", "depends": [0]},
          {"title": "Draft remediation plan", "agent": "agent_engineer", "depends": [0,1]},
        ]
    else:
        tasks = [
          {"title": "Research relevant context", "agent": "agent_research", "depends": []},
          {"title": "Create specialist draft", "agent": choose_agent(g), "depends": [0]},
          {"title": "Operations review and synthesis", "agent": "agent_ops", "depends": [1]},
        ]
    return tasks

def create_delegation(conn, workspace_id, goal):
    did = id_("dlg")
    ts = now()
    conn.execute("INSERT INTO delegations VALUES(?,?,?,?,?,?,?,?)",
                 (did,workspace_id,goal,"PLANNING","agent_ops",0,ts,ts))
    plan = plan_goal(goal)
    task_ids = []
    for item in plan:
        task_ids.append(id_("tsk"))
    for i,item in enumerate(plan):
        deps = [task_ids[d] for d in item["depends"]]
        action = goal if i == len(plan)-1 else None
        conn.execute("INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?)",
                     (task_ids[i],did,item["title"],item["agent"],"QUEUED",json.dumps(deps),action,None,ts,ts))
    conn.execute("UPDATE delegations SET status='RUNNING', updated_at=? WHERE id=?",(now(),did))
    emit(conn,workspace_id,"DELEGATION","INFO",f"Delegation created: {goal}",{"delegation_id":did,"tasks":len(plan)})
    conn.commit()
    advance(conn, did)
    return did

def dependencies_done(conn, task):
    deps = json.loads(task["depends_on"] or "[]")
    if not deps: return True
    rows = conn.execute(f"SELECT id,status FROM tasks WHERE id IN ({','.join('?'*len(deps))})",deps).fetchall()
    return len(rows)==len(deps) and all(r["status"]=="SUCCEEDED" for r in rows)

def advance(conn, delegation_id):
    dlg = conn.execute("SELECT * FROM delegations WHERE id=?",(delegation_id,)).fetchone()
    if not dlg: return
    workspace_id = dlg["workspace_id"]
    tasks = conn.execute("SELECT * FROM tasks WHERE delegation_id=? ORDER BY created_at,id",(delegation_id,)).fetchall()
    progressed = True
    while progressed:
        progressed = False
        for task in tasks:
            task = conn.execute("SELECT * FROM tasks WHERE id=?",(task["id"],)).fetchone()
            if task["status"] != "QUEUED" or not dependencies_done(conn,task):
                continue
            conn.execute("UPDATE tasks SET status='RUNNING', updated_at=? WHERE id=?",(now(),task["id"]))
            conn.execute("UPDATE agents SET status='RUNNING' WHERE id=?",(task["assigned_agent_id"],))
            emit(conn,workspace_id,"TASK","INFO",f"{task['title']} started",{"task_id":task["id"]})
            action = task["action"] or task["title"]
            decision = policy_decision(action, "SUPERVISED")
            if decision["decision"] == "REQUIRE_APPROVAL" and task["action"]:
                approval_id = id_("apr")
                conn.execute("UPDATE tasks SET status='WAITING_APPROVAL', updated_at=? WHERE id=?",(now(),task["id"]))
                conn.execute("INSERT INTO approvals VALUES(?,?,?,?,?,?,?,?)",
                             (approval_id,workspace_id,task["id"],action,decision["reason"],"PENDING",now(),None))
                conn.execute("UPDATE agents SET status='WAITING_APPROVAL' WHERE id=?",(task["assigned_agent_id"],))
                emit(conn,workspace_id,"APPROVAL","WARNING",f"Approval required: {action}",{"approval_id":approval_id})
            else:
                result = f"Completed by {task['assigned_agent_id']}: {task['title']}"
                conn.execute("UPDATE tasks SET status='SUCCEEDED', result=?, updated_at=? WHERE id=?",(result,now(),task["id"]))
                conn.execute("UPDATE agents SET status='IDLE', tasks_done=tasks_done+1, cost=cost+0.03 WHERE id=?",(task["assigned_agent_id"],))
                conn.execute("UPDATE delegations SET cost=cost+0.03, updated_at=? WHERE id=?",(now(),delegation_id))
                emit(conn,workspace_id,"TASK","INFO",f"{task['title']} completed",{"task_id":task["id"]})
            conn.commit()
            progressed = True
        tasks = conn.execute("SELECT * FROM tasks WHERE delegation_id=? ORDER BY created_at,id",(delegation_id,)).fetchall()
    statuses = [t["status"] for t in tasks]
    if statuses and all(s=="SUCCEEDED" for s in statuses):
        conn.execute("UPDATE delegations SET status='SUCCEEDED', updated_at=? WHERE id=?",(now(),delegation_id))
        emit(conn,workspace_id,"DELEGATION","INFO","Delegation completed",{"delegation_id":delegation_id})
        conn.commit()

def resolve_approval(conn, approval_id, approve: bool):
    approval = conn.execute("SELECT * FROM approvals WHERE id=?",(approval_id,)).fetchone()
    if not approval or approval["status"] != "PENDING": return False
    task = conn.execute("SELECT * FROM tasks WHERE id=?",(approval["task_id"],)).fetchone()
    status = "APPROVED" if approve else "REJECTED"
    conn.execute("UPDATE approvals SET status=?, resolved_at=? WHERE id=?",(status,now(),approval_id))
    if approve:
        conn.execute("UPDATE tasks SET status='SUCCEEDED', result=?, updated_at=? WHERE id=?",
                     (f"Approved and executed: {approval['action']}",now(),task["id"]))
        conn.execute("UPDATE agents SET status='IDLE', tasks_done=tasks_done+1, cost=cost+0.05 WHERE id=?",(task["assigned_agent_id"],))
        dlg = conn.execute("SELECT * FROM delegations WHERE id=?",(task["delegation_id"],)).fetchone()
        conn.execute("UPDATE delegations SET cost=cost+0.05, updated_at=? WHERE id=?",(now(),dlg["id"]))
        emit(conn,approval["workspace_id"],"APPROVAL","INFO",f"Approved: {approval['action']}",{"approval_id":approval_id})
        conn.commit(); advance(conn, task["delegation_id"])
    else:
        conn.execute("UPDATE tasks SET status='REJECTED', result='Rejected by human reviewer', updated_at=? WHERE id=?",(now(),task["id"]))
        conn.execute("UPDATE agents SET status='IDLE' WHERE id=?",(task["assigned_agent_id"],))
        conn.execute("UPDATE delegations SET status='REJECTED', updated_at=? WHERE id=?",(now(),task["delegation_id"]))
        emit(conn,approval["workspace_id"],"APPROVAL","WARNING",f"Rejected: {approval['action']}",{"approval_id":approval_id})
        conn.commit()
    return True
