"""
API Key Management System for borctakip application.
Provides secure API key generation, validation, and management.
"""

import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, List

# Database path
DB_PATH = 'debt_database'

# Constants
API_KEY_LENGTH = 32  # Length of the random part of the API key
KEY_PREFIX_LIVE = 'sk_live_'
KEY_PREFIX_TEST = 'sk_test_'


def _generate_api_key(key_type='live') -> Tuple[str, str]:
    """
    Generate a secure random API key.
    
    Args:
        key_type: Type of key ('live' or 'test')
        
    Returns:
        Tuple of (full_api_key, key_prefix)
        - full_api_key: The complete API key to show to user (only once)
        - key_prefix: The prefix to show in listings
    """
    # Generate secure random bytes
    random_part = secrets.token_urlsafe(API_KEY_LENGTH)
    
    # Choose prefix based on key type
    prefix = KEY_PREFIX_LIVE if key_type == 'live' else KEY_PREFIX_TEST
    
    # Construct full API key
    full_api_key = f"{prefix}{random_part}"
    
    # Create display prefix (first 12 characters)
    key_prefix = full_api_key[:12] + '...'
    
    return full_api_key, key_prefix


def _hash_api_key(api_key: str) -> str:
    """
    Hash an API key using SHA-256.
    
    Args:
        api_key: The plain text API key
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()


def create_api_key(user_id: str, key_name: str, key_type: str = 'live', 
                   expires_days: Optional[int] = None) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Create a new API key for a user.
    
    Args:
        user_id: The user's ID
        key_name: Descriptive name for the key
        key_type: Type of key ('live' or 'test'), defaults to 'live'
        expires_days: Optional number of days until expiration
        
    Returns:
        Tuple of (api_key, key_info) where:
        - api_key: The plain text API key (show only once!)
        - key_info: Dictionary with key metadata
        Returns (None, None) on failure
    """
    try:
        # Generate the API key
        full_api_key, key_prefix = _generate_api_key(key_type)
        
        # Hash the API key for storage
        hashed_key = _hash_api_key(full_api_key)
        
        # Get current timestamp
        created_at = datetime.now(timezone.utc).isoformat()
        
        # Calculate expiration if specified
        expires_at = None
        if expires_days:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=expires_days)).isoformat()
        
        # Insert into database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_keys 
            (user_id, key_name, api_key, key_prefix, created_at, is_active, expires_at)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        ''', (user_id, key_name, hashed_key, key_prefix, created_at, expires_at))
        
        key_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Prepare key info to return
        key_info = {
            'id': key_id,
            'user_id': user_id,
            'key_name': key_name,
            'key_prefix': key_prefix,
            'created_at': created_at,
            'expires_at': expires_at,
            'is_active': True
        }
        
        return full_api_key, key_info
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None, None
    except Exception as e:
        print(f"Error creating API key: {e}")
        return None, None


def validate_api_key(api_key: str) -> Optional[Dict]:
    """
    Validate an API key and return user information.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        Dictionary with user info and key metadata if valid, None otherwise
    """
    try:
        # Hash the provided API key
        hashed_key = _hash_api_key(api_key)
        
        # Query database
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, key_name, key_prefix, created_at, 
                   last_used_at, is_active, expires_at
            FROM api_keys
            WHERE api_key = ?
        ''', (hashed_key,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Convert to dictionary
        key_data = dict(row)
        
        # Check if key is active
        if not key_data['is_active']:
            conn.close()
            return None
        
        # Check if key has expired
        if key_data['expires_at']:
            expires_at = datetime.fromisoformat(key_data['expires_at'])
            if datetime.now(timezone.utc) > expires_at:
                conn.close()
                return None
        
        # Update last_used_at timestamp
        current_time = datetime.now(timezone.utc).isoformat()
        cursor.execute('''
            UPDATE api_keys
            SET last_used_at = ?
            WHERE id = ?
        ''', (current_time, key_data['id']))
        
        conn.commit()
        conn.close()
        
        # Update the returned data
        key_data['last_used_at'] = current_time
        
        return key_data
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error validating API key: {e}")
        return None


def revoke_api_key(key_id: int, user_id: str) -> bool:
    """
    Revoke (deactivate) an API key.
    
    Args:
        key_id: The ID of the API key to revoke
        user_id: The user ID (for authorization check)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Update the key to inactive (only if it belongs to the user)
        cursor.execute('''
            UPDATE api_keys
            SET is_active = 0
            WHERE id = ? AND user_id = ?
        ''', (key_id, user_id))
        
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return rows_affected > 0
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error revoking API key: {e}")
        return False


def delete_api_key(key_id: int, user_id: str) -> bool:
    """
    Permanently delete an API key.
    
    Args:
        key_id: The ID of the API key to delete
        user_id: The user ID (for authorization check)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Delete the key (only if it belongs to the user)
        cursor.execute('''
            DELETE FROM api_keys
            WHERE id = ? AND user_id = ?
        ''', (key_id, user_id))
        
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return rows_affected > 0
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error deleting API key: {e}")
        return False


def list_user_api_keys(user_id: str) -> List[Dict]:
    """
    List all API keys for a user (with masked keys).
    
    Args:
        user_id: The user's ID
        
    Returns:
        List of dictionaries containing key information
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, key_name, key_prefix, created_at, 
                   last_used_at, is_active, expires_at
            FROM api_keys
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        keys = [dict(row) for row in rows]
        
        return keys
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Error listing API keys: {e}")
        return []


def get_api_key_info(key_id: int, user_id: str) -> Optional[Dict]:
    """
    Get information about a specific API key.
    
    Args:
        key_id: The ID of the API key
        user_id: The user ID (for authorization check)
        
    Returns:
        Dictionary with key information or None if not found
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, key_name, key_prefix, created_at, 
                   last_used_at, is_active, expires_at
            FROM api_keys
            WHERE id = ? AND user_id = ?
        ''', (key_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error getting API key info: {e}")
        return None
