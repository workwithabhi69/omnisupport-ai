"""
Unit Tests for User Authentication & Role-Based Access Control.
"""

import os
import sys
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.sqlite_db import SQLiteManager


class TestAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use an in-memory or dedicated test db
        test_db_path = os.path.join(project_root, "data", "test_auth.db")
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        cls.test_db_path = test_db_path
        cls.db = SQLiteManager(db_path=test_db_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass

    def test_default_seeded_users(self):
        admin = self.db.get_user("admin")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "admin")

        customer = self.db.get_user("customer")
        self.assertIsNotNone(customer)
        self.assertEqual(customer["role"], "customer")

    def test_successful_authentication(self):
        ok, msg, user = self.db.authenticate_user("admin", "admin123")
        self.assertTrue(ok)
        self.assertEqual(user["username"], "admin")
        self.assertEqual(user["role"], "admin")

        ok2, msg2, user2 = self.db.authenticate_user("customer", "customer123")
        self.assertTrue(ok2)
        self.assertEqual(user2["username"], "customer")

    def test_invalid_password(self):
        ok, msg, user = self.db.authenticate_user("admin", "wrongpassword")
        self.assertFalse(ok)
        self.assertIsNone(user)

    def test_nonexistent_user(self):
        ok, msg, user = self.db.authenticate_user("nonexistent_user", "password")
        self.assertFalse(ok)

    def test_user_registration(self):
        ok, msg, user = self.db.register_user(
            username="testuser",
            password="testpass123",
            role="customer",
            full_name="Test Customer"
        )
        self.assertTrue(ok)
        self.assertEqual(user["username"], "testuser")

        # Test duplicate registration rejection
        ok_dup, msg_dup, _ = self.db.register_user("testuser", "anotherpass")
        self.assertFalse(ok_dup)
        self.assertIn("already exists", msg_dup)

        # Authenticate newly registered user
        auth_ok, _, auth_u = self.db.authenticate_user("testuser", "testpass123")
        self.assertTrue(auth_ok)
        self.assertEqual(auth_u["full_name"], "Test Customer")


if __name__ == "__main__":
    unittest.main()
