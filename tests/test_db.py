import unittest
import db


class TestDatabase(unittest.TestCase):
    def test_insert_and_query(self):
        db.create_tables()
        user_id = db.insert_user(
            "99999", "test", 30, "low", "renter", "uninsured")
        query_id = db.insert_query(user_id, "Test Policy")
        db.insert_response(query_id, "Test explanation.")
        results = db.get_all_responses()
        self.assertTrue(any("Test explanation." in r[3] for r in results))


if __name__ == "__main__":
    unittest.main()
