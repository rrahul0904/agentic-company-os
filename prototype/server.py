from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
import json, os
from db import connect, init_db, seed, now, emit
from engine import create_delegation, resolve_approval

ROOT = Path(__file__).parent
STATIC = ROOT / "static"
conn = connect(); init_db(conn); WORKSPACE_ID = seed(conn)

def rows(sql, params=()):
    with connect() as c:
        return [dict(r) for r in c.execute(sql,params).fetchall()]

def row(sql, params=()):
    with connect() as c:
        r=c.execute(sql,params).fetchone(); return dict(r) if r else None

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[http]", fmt % args)

    def send_json(self, data, status=200):
        body=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        p=urlparse(self.path).path
        if p == "/api/dashboard":
            agents=rows("SELECT * FROM agents WHERE workspace_id=? ORDER BY manager DESC, department,name",(WORKSPACE_ID,))
            delegations=rows("SELECT * FROM delegations WHERE workspace_id=? ORDER BY created_at DESC LIMIT 12",(WORKSPACE_ID,))
            approvals=rows("SELECT * FROM approvals WHERE workspace_id=? AND status='PENDING' ORDER BY created_at DESC",(WORKSPACE_ID,))
            workflows=rows("SELECT * FROM workflows WHERE workspace_id=? ORDER BY name",(WORKSPACE_ID,))
            events=rows("SELECT * FROM events WHERE workspace_id=? ORDER BY id DESC LIMIT 20",(WORKSPACE_ID,))
            brain=rows("SELECT * FROM brain_entries WHERE workspace_id=? ORDER BY id DESC",(WORKSPACE_ID,))
            task_count=row("SELECT COUNT(*) n FROM tasks WHERE status='SUCCEEDED'")["n"]
            cost=row("SELECT COALESCE(SUM(cost),0) n FROM delegations")["n"]
            active=sum(1 for a in agents if a["status"]!="IDLE")
            total_dlgs=len(rows("SELECT id FROM delegations WHERE workspace_id=?",(WORKSPACE_ID,)))
            ok_dlgs=len(rows("SELECT id FROM delegations WHERE workspace_id=? AND status='SUCCEEDED'",(WORKSPACE_ID,)))
            success=100 if total_dlgs==0 else round(ok_dlgs/total_dlgs*100,1)
            self.send_json({"workspace":row("SELECT * FROM workspaces WHERE id=?",(WORKSPACE_ID,)),"agents":agents,"delegations":delegations,"approvals":approvals,"workflows":workflows,"events":events,"brain":brain,"kpis":{"activeAgents":active,"tasksCompleted":task_count,"cost":round(cost,2),"successRate":success}}); return
        if p == "/api/health": self.send_json({"status":"ok","time":now()}); return
        if p in ["/","/index.html"]:
            data=(STATIC/"index.html").read_bytes(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data); return
        self.send_error(404)

    def body(self):
        n=int(self.headers.get("Content-Length","0")); return json.loads(self.rfile.read(n) or b"{}")

    def do_POST(self):
        p=urlparse(self.path).path; data=self.body()
        if p == "/api/delegations":
            goal=(data.get("goal") or "").strip()
            if not goal: self.send_json({"error":"goal required"},400); return
            with connect() as c: did=create_delegation(c,WORKSPACE_ID,goal)
            self.send_json({"id":did},201); return
        if p.startswith("/api/approvals/"):
            parts=p.split('/'); aid=parts[3]; action=parts[4] if len(parts)>4 else ''
            with connect() as c: ok=resolve_approval(c,aid,action=="approve")
            self.send_json({"ok":ok}); return
        if p == "/api/brain":
            title=(data.get("title") or "").strip(); content=(data.get("content") or "").strip(); kind=(data.get("kind") or "note").strip()
            if not title or not content: self.send_json({"error":"title and content required"},400); return
            with connect() as c:
                c.execute("INSERT INTO brain_entries(workspace_id,kind,title,content,created_at) VALUES(?,?,?,?,?)",(WORKSPACE_ID,kind,title,content,now()))
                emit(c,WORKSPACE_ID,"KNOWLEDGE","INFO",f"Business Brain updated: {title}")
                c.commit()
            self.send_json({"ok":True},201); return
        self.send_error(404)

if __name__ == "__main__":
    port=int(os.environ.get("PORT","8080"));
    print(f"Agentic Company OS prototype: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
