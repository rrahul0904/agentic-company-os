from __future__ import annotations
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).with_name("agentic_company_os.db")

def now():
    return datetime.now(timezone.utc).isoformat()

def connect(path: Path | None = None):
    conn = sqlite3.connect(path or DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS workspaces (
      id TEXT PRIMARY KEY, name TEXT NOT NULL, autonomy TEXT NOT NULL DEFAULT 'SUPERVISED', created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS brain_entries (
      id INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT NOT NULL, kind TEXT NOT NULL,
      title TEXT NOT NULL, content TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL,
      FOREIGN KEY(workspace_id) REFERENCES workspaces(id)
    );
    CREATE TABLE IF NOT EXISTS agents (
      id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, name TEXT NOT NULL, role TEXT NOT NULL,
      department TEXT NOT NULL, manager INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'IDLE',
      autonomy TEXT NOT NULL DEFAULT 'SUPERVISED', monthly_budget REAL NOT NULL DEFAULT 25,
      tasks_done INTEGER NOT NULL DEFAULT 0, cost REAL NOT NULL DEFAULT 0, created_at TEXT NOT NULL,
      FOREIGN KEY(workspace_id) REFERENCES workspaces(id)
    );
    CREATE TABLE IF NOT EXISTS delegations (
      id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, goal TEXT NOT NULL, status TEXT NOT NULL,
      manager_agent_id TEXT NOT NULL, cost REAL NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
      FOREIGN KEY(workspace_id) REFERENCES workspaces(id), FOREIGN KEY(manager_agent_id) REFERENCES agents(id)
    );
    CREATE TABLE IF NOT EXISTS tasks (
      id TEXT PRIMARY KEY, delegation_id TEXT NOT NULL, title TEXT NOT NULL, assigned_agent_id TEXT NOT NULL,
      status TEXT NOT NULL, depends_on TEXT NOT NULL DEFAULT '[]', action TEXT, result TEXT,
      created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
      FOREIGN KEY(delegation_id) REFERENCES delegations(id), FOREIGN KEY(assigned_agent_id) REFERENCES agents(id)
    );
    CREATE TABLE IF NOT EXISTS approvals (
      id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, task_id TEXT NOT NULL, action TEXT NOT NULL,
      reason TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, resolved_at TEXT,
      FOREIGN KEY(workspace_id) REFERENCES workspaces(id), FOREIGN KEY(task_id) REFERENCES tasks(id)
    );
    CREATE TABLE IF NOT EXISTS workflows (
      id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, name TEXT NOT NULL, trigger_type TEXT NOT NULL,
      status TEXT NOT NULL, runs INTEGER NOT NULL DEFAULT 0, success_rate REAL NOT NULL DEFAULT 100,
      created_at TEXT NOT NULL, FOREIGN KEY(workspace_id) REFERENCES workspaces(id)
    );
    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT NOT NULL, category TEXT NOT NULL,
      severity TEXT NOT NULL, message TEXT NOT NULL, payload TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL,
      FOREIGN KEY(workspace_id) REFERENCES workspaces(id)
    );
    """)
    conn.commit()

def seed(conn):
    ws = conn.execute("SELECT id FROM workspaces LIMIT 1").fetchone()
    if ws:
        return ws["id"]
    workspace_id = "ws_demo"
    conn.execute("INSERT INTO workspaces VALUES (?, ?, ?, ?)", (workspace_id, "Acme Agentic Co", "SUPERVISED", now()))
    agents = [
      ("agent_ops", "Nova", "Operations Lead", "Operations", 1),
      ("agent_research", "Atlas", "Research Analyst", "Research", 0),
      ("agent_content", "Mira", "Content Strategist", "Marketing", 0),
      ("agent_sales", "Jett", "Sales Specialist", "Sales", 0),
      ("agent_finance", "Sage", "Finance Analyst", "Finance", 0),
      ("agent_support", "Ember", "Customer Support", "Support", 0),
      ("agent_engineer", "Forge", "Engineering Assistant", "Engineering", 0),
      ("agent_brand", "Iris", "Brand Strategist", "Marketing", 0),
    ]
    for aid, name, role, dept, manager in agents:
        conn.execute("""INSERT INTO agents(id,workspace_id,name,role,department,manager,status,autonomy,monthly_budget,tasks_done,cost,created_at)
                        VALUES(?,?,?,?,?,?, 'IDLE','SUPERVISED',25,0,0,?)""",
                     (aid, workspace_id, name, role, dept, manager, now()))
    brain = [
      ("company", "Company", "We build governed AI automation for operations teams."),
      ("brand_voice", "Brand voice", "Clear, practical, evidence-first, confident without hype."),
      ("dont", "Do not", "Never send bulk messages, spend money, or modify production without approval."),
      ("goal", "Current goal", "Launch an enterprise-ready agent control plane."),
    ]
    for kind,title,content in brain:
        conn.execute("INSERT INTO brain_entries(workspace_id,kind,title,content,created_at) VALUES(?,?,?,?,?)",
                     (workspace_id,kind,title,content,now()))
    workflows = [
      ("wf_brief", "Morning Operations Brief", "SCHEDULED", "ACTIVE"),
      ("wf_research", "Weekly Market Scan", "SCHEDULED", "ACTIVE"),
      ("wf_lead", "Lead Qualification", "WEBHOOK", "ACTIVE"),
    ]
    for wid,name,trig,status in workflows:
        conn.execute("INSERT INTO workflows(id,workspace_id,name,trigger_type,status,created_at) VALUES(?,?,?,?,?,?)",
                     (wid, workspace_id,name,trig,status,now()))
    emit(conn, workspace_id, "SYSTEM", "INFO", "Workspace provisioned and starter agents deployed")
    conn.commit()
    return workspace_id

def emit(conn, workspace_id, category, severity, message, payload=None):
    conn.execute("INSERT INTO events(workspace_id,category,severity,message,payload,created_at) VALUES(?,?,?,?,?,?)",
                 (workspace_id,category,severity,message,json.dumps(payload or {}),now()))
    conn.commit()
