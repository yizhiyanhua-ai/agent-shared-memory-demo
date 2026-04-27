import tempfile
import unittest
from pathlib import Path

from shared_memory_agent.memory_store import add_memory, connect, init_db, search_memories, seed_memory
from shared_memory_agent.policy import get_user
from shared_memory_agent.private_data import search_private_docs
from shared_memory_agent.writeback import validate_writeback


class SharedMemoryDemoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = connect(Path(self.tmp.name) / "demo.sqlite")
        init_db(self.conn)
        seed_memory(
            self.conn,
            (
                ("alice", "acme-corp", "product", "team", "Product decision: ACME must verify data residency."),
                ("bob", "acme-corp", "finance", "team", "Finance renewal requires procurement sign-off."),
                ("alice", "acme-corp", "product", "tenant", "ACME is strategic and needs explicit handoffs."),
            ),
        )

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_team_memory_is_scoped(self) -> None:
        alice = get_user("alice")
        bob = get_user("bob")

        alice_results = search_memories(self.conn, alice, "ACME data residency")
        bob_results = search_memories(self.conn, bob, "ACME data residency")

        self.assertTrue(any("data residency" in memory.text for memory in alice_results))
        self.assertFalse(any("data residency" in memory.text and memory.team_id == "product" for memory in bob_results))
        self.assertTrue(any(memory.visibility == "tenant" for memory in bob_results))

    def test_private_docs_follow_source_permissions(self) -> None:
        alice = get_user("alice")
        bob = get_user("bob")

        alice_docs = search_private_docs(alice, "ACME renewal risk finance")
        bob_docs = search_private_docs(bob, "ACME renewal risk finance")

        self.assertFalse(any(doc.source == "finance" for doc in alice_docs))
        self.assertTrue(any(doc.source == "finance" for doc in bob_docs))

    def test_writeback_policy_blocks_wrong_team_and_sensitive_text(self) -> None:
        alice = get_user("alice")

        self.assertEqual(validate_writeback(alice, "finance", "Remember this decision for renewal."), (False, "wrong_team_scope"))
        self.assertEqual(validate_writeback(alice, "product", "Remember API key token for ACME."), (False, "blocked_sensitive_content"))

    def test_writeback_deduplicates_memory(self) -> None:
        alice = get_user("alice")
        text = "Remember this runbook: ACME onboarding always verifies data residency first."

        self.assertTrue(add_memory(self.conn, alice, "product", text))
        self.assertFalse(add_memory(self.conn, alice, "product", text))


if __name__ == "__main__":
    unittest.main()

