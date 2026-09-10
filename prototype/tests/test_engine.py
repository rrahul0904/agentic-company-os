import unittest, sqlite3, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from db import init_db, seed
from engine import policy_decision, create_delegation, resolve_approval

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.conn=sqlite3.connect(":memory:"); self.conn.row_factory=sqlite3.Row; self.conn.execute("PRAGMA foreign_keys=ON")
        init_db(self.conn); self.ws=seed(self.conn)
    def tearDown(self): self.conn.close()
    def test_safe_action_allowed(self):
        self.assertEqual(policy_decision("research competitor pricing")["decision"],"ALLOW")
    def test_sensitive_action_requires_approval(self):
        self.assertEqual(policy_decision("send campaign email to all leads")["decision"],"REQUIRE_APPROVAL")
    def test_delegation_completes_without_sensitive_action(self):
        did=create_delegation(self.conn,self.ws,"research a new market opportunity")
        status=self.conn.execute("select status from delegations where id=?",(did,)).fetchone()[0]
        self.assertEqual(status,"SUCCEEDED")
    def test_sensitive_delegation_waits_then_resolves(self):
        did=create_delegation(self.conn,self.ws,"launch campaign and send email to all leads")
        a=self.conn.execute("select * from approvals where status='PENDING'").fetchone()
        self.assertIsNotNone(a)
        self.assertTrue(resolve_approval(self.conn,a["id"],True))
        status=self.conn.execute("select status from delegations where id=?",(did,)).fetchone()[0]
        self.assertEqual(status,"SUCCEEDED")

if __name__=='__main__': unittest.main()
