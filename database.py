import sqlite3
from typing import List, Dict
from datetime import datetime


class ChatDatabase:
    def __init__(self, db_path: str = 'chat_history.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Create and return a database connection"""
        conn = sqlite3.connect(self.db_path)
        # Enable foreign keys and return dictionary-like rows
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             session_id TEXT NOT NULL,
             content TEXT NOT NULL,
             role TEXT NOT NULL,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')
        conn.commit()
        conn.close()

    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session, formatted for template display"""
        conn = self.get_connection()
        c = conn.cursor()

        # Get messages ordered by timestamp
        c.execute('''
            SELECT content, role, timestamp 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp
        ''', (session_id,))

        # Convert to list of dicts in the format expected by the template
        messages = [
            {
                'content': row['content'],
                'role': row['role'],
                'timestamp': row['timestamp']
            }
            for row in c.fetchall()
        ]

        conn.close()
        return messages

    def save_message(self, session_id: str, content: str, role: str):
        """Save a message to the database and return the message ID"""
        if role not in ['user', 'ai']:
            raise ValueError("Role must be either 'user' or 'ai'")
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO messages (session_id, content, role) 
            VALUES (?, ?, ?)
        ''', (session_id, content, role))
        message_id = c.lastrowid  # Get the ID of the inserted row
        conn.commit()
        conn.close()

        return message_id

    def delete_chat_history(self, session_id: str):
        """Delete all messages for a given session"""
        conn = self.get_connection()
        c = conn.cursor()

        c.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))

        conn.commit()
        conn.close()


# Create a singleton instance
db = ChatDatabase()
