import sqlite3

DB_NAME = "civicbridge.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_tables():
    with connect() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zip_code TEXT NOT NULL,
                role TEXT NOT NULL,
                age INTEGER,
                income_bracket TEXT,
                housing_status TEXT,
                healthcare_access TEXT
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                policy_title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id INTEGER NOT NULL,
                explanation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(query_id) REFERENCES queries(id)
            );
        """)
        conn.commit()


def insert_user(zip_code, role, age=None, income_bracket=None, housing_status=None, healthcare_access=None):
    with connect() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (zip_code, role, age, income_bracket, housing_status, healthcare_access)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (zip_code, role, age, income_bracket, housing_status, healthcare_access))
        conn.commit()
        return c.lastrowid


def insert_query(user_id, policy_title):
    with connect() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO queries (user_id, policy_title) VALUES (?, ?)",
                  (user_id, policy_title))
        conn.commit()
        return c.lastrowid


def insert_response(query_id, explanation):
    with connect() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO responses (query_id, explanation) VALUES (?, ?)",
                  (query_id, explanation))
        conn.commit()


def get_all_responses(limit=None):
    with connect() as conn:
        c = conn.cursor()
        query = """
            SELECT users.zip_code, users.role, queries.policy_title, responses.explanation
            FROM responses
            JOIN queries ON responses.query_id = queries.id
            JOIN users ON queries.user_id = users.id
            ORDER BY responses.created_at DESC
        """
        if limit is not None:
            query += " LIMIT ?"
            c.execute(query, (limit,))
        else:
            c.execute(query)
        return c.fetchall()


if __name__ == "__main__":
    create_tables()
    print("Database initialized.")
