import sqlite3
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


DB_NAME = "civicbridge.db"


def connect():
    """Create database connection."""
    return sqlite3.connect(DB_NAME)


def create_tables():
    """Create all necessary tables for CivicBridge."""
    with connect() as conn:
        c = conn.cursor()

        #Chat history - same-session chats
        c.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                message_type TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        print("Chat history table created successfully")

        #c.execute(
            #CREATE TABLE IF NOT EXISTS responses (
                #id INTEGER PRIMARY KEY AUTOINCREMENT,
                #query_id INTEGER NOT NULL,
                #explanation TEXT NOT NULL,
                #created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                #FOREIGN KEY(query_id) REFERENCES queries(id)
            #);
        #)
        #conn.commit()

"""CHAT HISTORY FUNCTIONS - for storing chat messages in a session"""

def save_chat_message(session_id: str, user_message: str, bot_response: str, message_type: str = 'general'):
    """Save chat conversation for session history."""
    try:
        with connect() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO chat_history (session_id, user_message, bot_response, message_type)
                VALUES (?, ?, ?, ?)
            """, (session_id, user_message, bot_response, message_type))
            conn.commit()
    except Exception as e:
        print(f"Error saving chat message: {e}")

def get_chat_history(session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get chat history for the session (for scrolling up in chat)."""
    try: 
        with connect() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT user_message, bot_response, message_type, created_at
                FROM chat_history
                WHERE session_id = ?
                ORDER BY created_at ASC
                LIMIT ?
            """, (session_id, limit))

            rows = c.fetchall()
            return [{
                'user_message': row[0],
                'bot_response': row[1],
                'message_type': row[2],
                'created_at': row[3]
            } for row in rows]
            
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []

def get_recent_chat_context(session_id: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Get recent chat messages for AI context (last few messages)."""
    try:
        with connect() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT user_message, bot_response, message_type, created_at
                FROM chat_history
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (session_id, limit))

            rows = c.fetchall()
            return [{
                'user_message': row[0],
                'bot_response': row[1],
                'message_type': row[2],
                'created_at': row[3]
            } for row in rows] #[::-1]  # Not too sure if we should reverse to maintain chronological order
            
    except Exception as e:
        print(f"Error getting recent chat context: {e}")
        return []

def clear_chat_history(session_id: str):
    """Remove chat history for a specific session."""
    try:
        with connect() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            deleted_count = c.rowcount
            conn.commit()
            print(f"Cleaned up {deleted_count} messages for session {session_id}")
    except Exception as e:
        print(f"Error cleaning up session chat: {e}")

if __name__ == "__main__":
    create_tables()
    print("Database initialized.")



""" THESE FUNCTIONS ARE FROM CLI PROJECT"""

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
    
"""END OF CLI FUNCTIONS"""
