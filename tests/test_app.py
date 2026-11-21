"""
Unit and Integration Tests for Offline Customer Support Chat Application.
"""

import unittest
from PyQt5.QtWidgets import QApplication
from config import AppConfig, load_config, save_config
from services.history_manager import HistoryManager
from services.n8n_client import N8nChatWorker, BackendHealthChecker

# Create single QApplication instance for widget tests
app = QApplication.instance() or QApplication([])


class TestConfig(unittest.TestCase):
    def test_default_config(self):
        cfg = AppConfig()
        self.assertIn("localhost:5678", cfg.n8n_webhook_url)
        self.assertIn("bd156e94-be53-47cf-85c4-0b3999089d3c", cfg.n8n_webhook_url)
        self.assertEqual(cfg.get_effective_webhook_url(), cfg.n8n_webhook_url)

    def test_test_endpoint_switch(self):
        cfg = AppConfig(use_test_endpoint=True)
        self.assertIn("webhook-test", cfg.get_effective_webhook_url())


class TestHistoryManager(unittest.TestCase):
    def setUp(self):
        self.hm = HistoryManager()

    def test_create_and_add_message(self):
        session = self.hm.create_session("Test Session")
        sid = session["id"]
        self.assertIsNotNone(sid)

        # Add user message
        msg1 = self.hm.add_message(sid, "user", "Where is my order ORD1001?")
        self.assertEqual(msg1["sender"], "user")

        # Add bot message with ticket metadata
        msg2 = self.hm.add_message(
            sid, "bot",
            "Your ticket TKT-1001 has been registered.",
            metadata={"ticket_id": "TKT-1001", "order_id": "ORD1001"}
        )
        self.assertEqual(msg2["sender"], "bot")
        self.assertEqual(msg2["metadata"]["ticket_id"], "TKT-1001")

        # Verify session retrieval
        retrieved = self.hm.get_session(sid)
        self.assertEqual(len(retrieved["messages"]), 2)

        # Clean up
        self.hm.delete_session(sid)


class TestN8nParsing(unittest.TestCase):
    def test_ticket_id_extraction(self):
        worker = N8nChatWorker(
            webhook_url="http://localhost:5678/webhook/test",
            message="Hi",
            session_id="test"
        )
        text = "I have filed your complaint with ticket ID TKT-998822."
        self.assertEqual(worker._extract_ticket_id(text), "TKT-998822")

        text_millis = "Ticket created: TKT-1728738291000 successfully."
        self.assertEqual(worker._extract_ticket_id(text_millis), "TKT-1728738291000")

    def test_order_id_extraction(self):
        worker = N8nChatWorker(
            webhook_url="http://localhost:5678/webhook/test",
            message="Hi",
            session_id="test"
        )
        text = "Order details for ORD1001: product is Wireless Mouse, status is Shipped."
        self.assertEqual(worker._extract_order_id(text), "ORD1001")


class TestHealthChecker(unittest.TestCase):
    def test_local_services(self):
        cfg = AppConfig()
        results = BackendHealthChecker.check_all(cfg)
        self.assertIn("n8n_ok", results)
        self.assertIn("ollama_ok", results)
        self.assertIn("webhook_ok", results)
        print("Live Health Results:", results)


if __name__ == "__main__":
    unittest.main()
