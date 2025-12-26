"""
Database initialization script for API key management system.
Creates the api_keys table in the debt_database SQLite database.
"""

import sqlite3
import os

def init_api_keys_table(db_path='debt_database'):
    """
    Initialize the api_keys table in the database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create api_keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                key_name TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                key_prefix TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_used_at TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                expires_at TEXT
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_api_keys_user_id 
            ON api_keys(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_api_keys_api_key 
            ON api_keys(api_key)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_api_keys_is_active 
            ON api_keys(is_active)
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✓ API keys table initialized successfully in {db_path}")
        return True
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    # Initialize the table in the main database
    success = init_api_keys_table('debt_database')
    
    if success:
        print("\nDatabase schema is ready for API key management!")
        print("\nYou can now use the API key management functions:")
        print("  - create_api_key(user_id, key_name)")
        print("  - validate_api_key(api_key)")
        print("  - revoke_api_key(key_id, user_id)")
        print("  - list_user_api_keys(user_id)")
    else:
        print("\nFailed to initialize database schema.")
