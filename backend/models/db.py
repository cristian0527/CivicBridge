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

        # Representative cache table - stores senators + local reps
        c.execute("""
            CREATE TABLE IF NOT EXISTS representative_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zip_code TEXT NOT NULL,
                bioguide_id TEXT NOT NULL,
                name TEXT NOT NULL,
                party TEXT,
                chamber TEXT, -- 'Representative' or 'Senator'
                district TEXT, -- District number for House reps, NULL for senators
                state TEXT NOT NULL,
                seniority TEXT, -- 'senior', 'junior', or NULL for House reps
                phone TEXT,
                office_address TEXT,
                website TEXT,
                contact_form TEXT,
                twitter TEXT,
                facebook TEXT,
                youtube TEXT,
                photo_url TEXT,
                recent_bills TEXT, -- JSON string with recent sponsored bills
                recent_votes TEXT, -- JSON string with recent votes
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP DEFAULT (datetime('now', '+1 day')),
                UNIQUE(zip_code, bioguide_id)
            );
        """)
        
        # Index for faster lookups
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_rep_cache_zip_expires 
            ON representative_cache(zip_code, expires_at);
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

    """REPRESENTATIVE CACHE FUNCTIONS"""
def cache_representatives(zip_code: str, representatives: List[Dict[str, Any]]):
    """
    Cache representative data for a ZIP code.
    Stores both senators and local House representative.
    """
    try:
        with connect() as conn:
            c = conn.cursor()

            c.execute("DELETE FROM representative_cache WHERE zip_code = ?", (zip_code,))
            for rep in representatives:
                # Extract social media info
                social = rep.get('social', {}) if isinstance(rep.get('social'), dict) else {}

                c.execute("""
                    INSERT OR REPLACE INTO representative_cache
                    (zip_code, bioguide_id, name, party, chamber, district, state, seniority,
                    phone, office_address, website, contact_form, twitter, facebook, youtube,
                    photo_url, recent_bills, recent_votes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                          """, (
                                zip_code,
                                rep.get('bioguide_id'),
                                rep.get('name'),
                                rep.get('party'),
                                rep.get('chamber'),
                                rep.get('district'),
                                rep.get('state'),
                                rep.get('seniority'),
                                rep.get('phone'),
                                rep.get('address'),
                                rep.get('website'),
                                rep.get('contact_form'),
                                rep.get('twitter') or social.get('twitter'),
                                social.get('facebook'),
                                social.get('youtube'),
                                rep.get('photo_url'),
                                json.dumps(rep.get('recent_bills', [])),
                                json.dumps(rep.get('recent_votes', []))
                          ))
            conn.commit()
            print(f"Cached {len(representatives)} representatives for ZIP code {zip_code}")
    except Exception as e:
        print(f"Error caching representatives: {e}")

def get_cached_representatives(zip_code: str) -> Optional[List[Dict[str, Any]]]:
    """Get cached representatives for a ZIP code."""
    try:
        with connect() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT bioguide_id, name, party, chamber, district, state, seniority,
                       phone, office_address, website, contact_form, twitter,
                       facebook, youtube, photo_url, recent_bills, recent_votes, created_at
                FROM representative_cache
                WHERE zip_code = ? AND expires_at > datetime('now')
                ORDER BY
                    CASE chamber
                        WHEN 'Representative' THEN 1
                        WHEN 'Senator' THEN 2
                    END,
                      CASE seniority
                        WHEN 'senior' THEN 1
                        WHEN 'junior' THEN 2
                        ELSE 3
                    END
            """, (zip_code,))
            rows = c.fetchall()
            if not rows:
                return None
            
            representatives = []
            for row in rows:
                rep = {
                    'bioguide_id': row[0],
                    'name': row[1],
                    'party': row[2],
                    'chamber': row[3],
                    'district': row[4],
                    'state': row[5],
                    'seniority': row[6],
                    'phone': row[7],
                    'office_address': row[8],
                    'website': row[9],
                    'contact_form': row[10],
                    'twitter': row[11],
                    'facebook': row[12],
                    'youtube': row[13],
                    'photo_url': row[14],
                    'recent_bills': json.loads(row[15]) if row[15] else [],
                    'recent_votes': json.loads(row[16]) if row[16] else [],
                    'cached_at': row[17],
                    'source': 'cache'
                }

                representatives.append(rep)
            print(f"Retrieved {len(representatives)} cached representatives for ZIP code {zip_code}")
            return representatives
    except Exception as e:
        print(f"Error retrieving cached representatives: {e}")
        return None

def get_representatives_by_type(zip_code: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get cached representatives grouped by chamber type (House/Senate).
    Returns a dictionary with 'House' and 'Senate' keys.
    """
    all_reps = get_cached_representatives(zip_code)
    if not all_reps:
        return {'senators': [], 'representative': []}

    grouped = {'House': [], 'Senate': []}
    senators = [rep for rep in all_reps if rep['chamber'] == 'Senator']
    house_reps = [rep for rep in all_reps if rep['chamber'] == 'Representative']

    return {
        'senators': senators,
        'representative': house_reps
    }

def update_representative_congress_data(zip_code: str, bioguide_id: str, bills: List[Dict], votes: List[Dict]):
    """Update the expiration date for a specific representative in the cache."""
    try:
        with connect() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE representative_cache
                SET recent_bills = ?, recent_votes = ?, expires_at = datetime('now', '+1 day')
                WHERE zip_code = ? AND bioguide_id = ?
            """, (
                json.dumps(bills),
                json.dumps(votes),
                zip_code,
                bioguide_id
            ))

            if c.rowcount > 0:
                conn.commit()
                print(f"Updated representative {bioguide_id} for ZIP code {zip_code}")
            else:
                print(f"No cached representative found for ZIP {zip_code} with Bioguide ID {bioguide_id}")
    except Exception as e:
        print(f"Error updating representative cache: {e}")
 
def cleanup_expired_representatives():
    """Remove expired representative cache entries."""
    try:
        with connect() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM representative_cache WHERE expires_at < datetime('now')")
            deleted_count = c.rowcount
            conn.commit()
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} expired representative cache entries")
    except Exception as e:
        print(f"Error cleaning up expired representatives: {e}")

def get_cache_stats() -> Dict[str, Any]:
    """Get statistics about the representative cache."""
    try:
        with connect() as conn:
            c = conn.cursor()
            
            # Total cached representatives
            c.execute("SELECT COUNT(*) FROM representative_cache")
            total_reps = c.fetchone()[0]
            
            # Unique ZIP codes cached
            c.execute("SELECT COUNT(DISTINCT zip_code) FROM representative_cache")
            unique_zips = c.fetchone()[0]
            
            # Active (non-expired) cache entries
            c.execute("SELECT COUNT(*) FROM representative_cache WHERE expires_at > datetime('now')")
            active_reps = c.fetchone()[0]
            
            # Senators vs House reps
            c.execute("SELECT chamber, COUNT(*) FROM representative_cache WHERE expires_at > datetime('now') GROUP BY chamber")
            chamber_counts = dict(c.fetchall())
            
            return {
                'total_representatives': total_reps,
                'unique_zip_codes': unique_zips,
                'active_entries': active_reps,
                'senators': chamber_counts.get('Senator', 0),
                'house_representatives': chamber_counts.get('Representative', 0)
            }
            
    except Exception as e:
        print(f"Error getting cache stats: {e}")
        return {}


"""CLEANUP FUNCTIONS"""

def cleanup_expired_data():
    """Remove expired sessions, cache data, and old chat history."""
    try:
        with connect() as conn:
            c = conn.cursor()
            
            # Clean expired representative cache
            c.execute("DELETE FROM representative_cache WHERE expires_at < datetime('now')")
            reps_deleted = c.rowcount
            
            # Clean old chat history (older than 7 days)
            c.execute("""
                DELETE FROM chat_history 
                WHERE created_at < datetime('now', '-7 days')
            """)
            chat_deleted = c.rowcount
            
            conn.commit()
            print(f"Cleanup: {reps_deleted} expired reps, {chat_deleted} old chats")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")


"""HELPER FUNCTIONS FOR FLASK INTEGRATION"""
def get_representatives_with_cache(zip_code: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Get representatives using cache-first strategy. Return lists of senators and representatives."""
    if not force_refresh:
        # Try cache first
        cached_reps = get_cached_representatives(zip_code)
        if cached_reps:
            return cached_reps
    
    # Cache miss or forced refresh - fetch from APIs
    try:
        # This would be called from your Flask route
        # You'll need to import and use your API clients here
        print(f"Cache miss for ZIP {zip_code} - would fetch from APIs")
        return []  # Placeholder - implement API calls in your Flask route
        
    except Exception as e:
        print(f"Error fetching representatives: {e}")
        return []


if __name__ == "__main__":
    create_tables()
    print("Database initialized.")
    
    # Test the database with sample data
    test_zip = "12601"
    
    # Sample representatives data (matches your Geocodio output format)
    test_reps = [
        {
            'bioguide_id': 'R000579',
            'name': 'Patrick Ryan',
            'party': 'Democrat',
            'chamber': 'Representative',
            'district': '18',
            'state': 'NY',
            'seniority': None,
            'phone': '202-225-5614',
            'address': '1708 Longworth House Office Building Washington DC 20515-3218',
            'website': 'https://patryan.house.gov',
            'contact_form': None,
            'twitter': 'RepPatRyanNY',
            'photo_url': 'https://www.congress.gov/img/member/r000579_200.jpg'
        },
        {
            'bioguide_id': 'S000148',
            'name': 'Charles Schumer',
            'party': 'Democrat',
            'chamber': 'Senator',
            'district': None,
            'state': 'NY',
            'seniority': 'senior',
            'phone': '202-224-6542',
            'address': '322 Hart Senate Office Building Washington DC 20510',
            'website': 'https://www.schumer.senate.gov',
            'contact_form': 'https://www.schumer.senate.gov/contact/email-chuck',
            'twitter': 'SenSchumer',
            'photo_url': 'https://www.congress.gov/img/member/s000148_200.jpg'
        },
        {
            'bioguide_id': 'G000555',
            'name': 'Kirsten Gillibrand',
            'party': 'Democrat',
            'chamber': 'Senator',
            'district': None,
            'state': 'NY',
            'seniority': 'junior',
            'phone': '202-224-4451',
            'address': '478 Russell Senate Office Building Washington DC 20510',
            'website': 'https://www.gillibrand.senate.gov',
            'contact_form': 'https://www.gillibrand.senate.gov/contact/email-me',
            'twitter': 'GillibrandNY',
            'photo_url': 'https://www.congress.gov/img/member/g000555_200.jpg'
        }
    ]
    
    # Test caching
    cache_representatives(test_zip, test_reps)
    
    # Test retrieval
    cached = get_cached_representatives(test_zip)
    if cached:
        print(f"Retrieved {len(cached)} representatives from cache")
    else:
        print("No cached representatives found")

    
    # Test organized retrieval  
    organized = get_representatives_by_type(test_zip)
    print(f"Senators: {len(organized['senators'])}, House Rep: {len(organized['representative'])}")
    
    # Test stats
    stats = get_cache_stats()
    print(f"Cache stats: {stats}")
    
    print("Database initialized with representative caching.")




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
