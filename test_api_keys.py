"""
Unit tests for API Key Management System.
Tests key generation, validation, revocation, and authentication.
"""

import unittest
import sqlite3
import os
import time
from datetime import datetime, timedelta, timezone
from api_key_manager import (
    create_api_key,
    validate_api_key,
    list_user_api_keys,
    revoke_api_key,
    delete_api_key,
    get_api_key_info,
    _generate_api_key,
    _hash_api_key
)
from api_auth_middleware import (
    authenticate_api_request,
    check_api_auth
)
from init_api_keys_db import init_api_keys_table


class TestAPIKeyManagement(unittest.TestCase):
    """Test cases for API key management functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests."""
        cls.test_db = 'test_api_keys.db'
        
        # Update module to use test database
        import api_key_manager
        api_key_manager.DB_PATH = cls.test_db
        
        import api_auth_middleware
        import importlib
        importlib.reload(api_auth_middleware)
    
    def setUp(self):
        """Set up before each test."""
        # Remove test database if it exists
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        
        # Initialize database
        init_api_keys_table(self.test_db)
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove test database
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_generate_api_key_format(self):
        """Test that API keys are generated with correct format."""
        # Test live key
        live_key, live_prefix = _generate_api_key('live')
        self.assertTrue(live_key.startswith('sk_live_'))
        self.assertTrue(live_prefix.startswith('sk_live_'))
        self.assertTrue(live_prefix.endswith('...'))
        
        # Test test key
        test_key, test_prefix = _generate_api_key('test')
        self.assertTrue(test_key.startswith('sk_test_'))
        self.assertTrue(test_prefix.startswith('sk_test_'))
        
        # Check length
        self.assertGreater(len(live_key), 40)
        self.assertGreater(len(test_key), 40)
    
    def test_generate_api_key_uniqueness(self):
        """Test that generated API keys are unique."""
        keys = set()
        for _ in range(100):
            key, _ = _generate_api_key()
            keys.add(key)
        
        # All keys should be unique
        self.assertEqual(len(keys), 100)
    
    def test_hash_api_key(self):
        """Test API key hashing."""
        key = "sk_live_test_key_12345"
        hash1 = _hash_api_key(key)
        hash2 = _hash_api_key(key)
        
        # Same key should produce same hash
        self.assertEqual(hash1, hash2)
        
        # Hash should be 64 characters (SHA-256 hex)
        self.assertEqual(len(hash1), 64)
        
        # Different keys should produce different hashes
        different_key = "sk_live_test_key_67890"
        hash3 = _hash_api_key(different_key)
        self.assertNotEqual(hash1, hash3)
    
    def test_create_api_key_success(self):
        """Test successful API key creation."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        self.assertIsNotNone(api_key)
        self.assertIsNotNone(key_info)
        self.assertTrue(api_key.startswith('sk_live_'))
        self.assertEqual(key_info['user_id'], 'user123')
        self.assertEqual(key_info['key_name'], 'Test Key')
        self.assertTrue(key_info['is_active'])
        self.assertIsNotNone(key_info['created_at'])
    
    def test_create_test_api_key(self):
        """Test creation of test API key."""
        api_key, key_info = create_api_key('user456', 'Test Env', key_type='test')
        
        self.assertIsNotNone(api_key)
        self.assertTrue(api_key.startswith('sk_test_'))
        self.assertTrue(key_info['key_prefix'].startswith('sk_test_'))
    
    def test_create_api_key_with_expiration(self):
        """Test API key creation with expiration."""
        api_key, key_info = create_api_key('user789', 'Temp Key', expires_days=7)
        
        self.assertIsNotNone(api_key)
        self.assertIsNotNone(key_info['expires_at'])
        
        # Check expiration date is roughly 7 days from now
        expires = datetime.fromisoformat(key_info['expires_at'])
        expected = datetime.now(timezone.utc) + timedelta(days=7)
        delta = abs((expires - expected).total_seconds())
        self.assertLess(delta, 5)  # Within 5 seconds
    
    def test_validate_api_key_success(self):
        """Test successful API key validation."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Validate the key
        validated = validate_api_key(api_key)
        
        self.assertIsNotNone(validated)
        self.assertEqual(validated['user_id'], 'user123')
        self.assertEqual(validated['key_name'], 'Test Key')
        self.assertTrue(validated['is_active'])
        self.assertIsNotNone(validated['last_used_at'])
    
    def test_validate_api_key_invalid(self):
        """Test validation of invalid API key."""
        result = validate_api_key('sk_live_invalid_key_12345')
        self.assertIsNone(result)
    
    def test_validate_api_key_updates_last_used(self):
        """Test that validation updates last_used_at timestamp."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # First validation
        result1 = validate_api_key(api_key)
        last_used_1 = result1['last_used_at']
        
        # Wait a moment
        time.sleep(0.1)
        
        # Second validation
        result2 = validate_api_key(api_key)
        last_used_2 = result2['last_used_at']
        
        # Last used should be updated
        self.assertNotEqual(last_used_1, last_used_2)
    
    def test_validate_inactive_key(self):
        """Test that inactive keys fail validation."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Revoke the key
        revoke_api_key(key_info['id'], 'user123')
        
        # Try to validate
        result = validate_api_key(api_key)
        self.assertIsNone(result)
    
    def test_validate_expired_key(self):
        """Test that expired keys fail validation."""
        # Create key that expires in 1 second
        api_key, key_info = create_api_key('user123', 'Test Key', expires_days=-1)
        
        # Key should be expired
        result = validate_api_key(api_key)
        self.assertIsNone(result)
    
    def test_list_user_api_keys(self):
        """Test listing user's API keys."""
        # Create multiple keys
        create_api_key('user123', 'Key 1')
        create_api_key('user123', 'Key 2')
        create_api_key('user456', 'Key 3')
        
        # List keys for user123
        keys = list_user_api_keys('user123')
        
        self.assertEqual(len(keys), 2)
        key_names = [k['key_name'] for k in keys]
        self.assertIn('Key 1', key_names)
        self.assertIn('Key 2', key_names)
        self.assertNotIn('Key 3', key_names)
    
    def test_list_user_api_keys_empty(self):
        """Test listing keys for user with no keys."""
        keys = list_user_api_keys('nonexistent_user')
        self.assertEqual(len(keys), 0)
    
    def test_revoke_api_key_success(self):
        """Test successful key revocation."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Revoke the key
        success = revoke_api_key(key_info['id'], 'user123')
        self.assertTrue(success)
        
        # Key should not validate
        result = validate_api_key(api_key)
        self.assertIsNone(result)
        
        # Key should still be in list but inactive
        keys = list_user_api_keys('user123')
        self.assertEqual(len(keys), 1)
        self.assertFalse(keys[0]['is_active'])
    
    def test_revoke_api_key_wrong_user(self):
        """Test that users can't revoke other users' keys."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Try to revoke with wrong user
        success = revoke_api_key(key_info['id'], 'user456')
        self.assertFalse(success)
        
        # Key should still be valid
        result = validate_api_key(api_key)
        self.assertIsNotNone(result)
    
    def test_delete_api_key_success(self):
        """Test successful key deletion."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Delete the key
        success = delete_api_key(key_info['id'], 'user123')
        self.assertTrue(success)
        
        # Key should not be in list
        keys = list_user_api_keys('user123')
        self.assertEqual(len(keys), 0)
    
    def test_delete_api_key_wrong_user(self):
        """Test that users can't delete other users' keys."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Try to delete with wrong user
        success = delete_api_key(key_info['id'], 'user456')
        self.assertFalse(success)
        
        # Key should still exist
        keys = list_user_api_keys('user123')
        self.assertEqual(len(keys), 1)
    
    def test_get_api_key_info(self):
        """Test getting API key information."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Get key info
        info = get_api_key_info(key_info['id'], 'user123')
        
        self.assertIsNotNone(info)
        self.assertEqual(info['key_name'], 'Test Key')
        self.assertEqual(info['user_id'], 'user123')
    
    def test_get_api_key_info_wrong_user(self):
        """Test that users can't get other users' key info."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Try to get info with wrong user
        info = get_api_key_info(key_info['id'], 'user456')
        self.assertIsNone(info)
    
    def test_authenticate_request_success(self):
        """Test successful request authentication."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Authenticate request
        auth_header = f"Bearer {api_key}"
        auth_context = authenticate_api_request(auth_header)
        
        self.assertIsNotNone(auth_context)
        self.assertEqual(auth_context['user_id'], 'user123')
        self.assertEqual(auth_context['key_name'], 'Test Key')
        self.assertTrue(auth_context['authenticated'])
    
    def test_authenticate_request_no_header(self):
        """Test authentication with no header."""
        result = authenticate_api_request(None)
        self.assertIsNone(result)
    
    def test_authenticate_request_invalid_format(self):
        """Test authentication with invalid header format."""
        result = authenticate_api_request("InvalidFormat")
        self.assertIsNone(result)
        
        result = authenticate_api_request("Basic user:pass")
        self.assertIsNone(result)
    
    def test_authenticate_request_invalid_key(self):
        """Test authentication with invalid key."""
        auth_header = "Bearer sk_live_invalid_key_12345"
        result = authenticate_api_request(auth_header)
        self.assertIsNone(result)
    
    def test_check_api_auth(self):
        """Test check_api_auth helper function."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Valid key
        is_auth, context = check_api_auth(f"Bearer {api_key}")
        self.assertTrue(is_auth)
        self.assertIsNotNone(context)
        self.assertEqual(context['user_id'], 'user123')
        
        # Invalid key
        is_auth, context = check_api_auth("Bearer invalid")
        self.assertFalse(is_auth)
        self.assertIsNone(context)
        
        # No header
        is_auth, context = check_api_auth(None)
        self.assertFalse(is_auth)
        self.assertIsNone(context)
    
    def test_api_key_not_stored_plaintext(self):
        """Test that API keys are not stored in plaintext."""
        api_key, key_info = create_api_key('user123', 'Test Key')
        
        # Query database directly
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT api_key FROM api_keys WHERE id = ?', (key_info['id'],))
        stored_key = cursor.fetchone()[0]
        conn.close()
        
        # Stored key should not match plaintext
        self.assertNotEqual(stored_key, api_key)
        
        # Stored key should be a hash (64 chars)
        self.assertEqual(len(stored_key), 64)


class TestAPIKeyEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        cls.test_db = 'test_api_keys_edge.db'
        
        # Update module to use test database
        import api_key_manager
        api_key_manager.DB_PATH = cls.test_db
    
    def setUp(self):
        """Set up before each test."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        init_api_keys_table(self.test_db)
    
    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_create_key_with_empty_name(self):
        """Test creating key with empty name."""
        api_key, key_info = create_api_key('user123', '')
        # Should still work, name is just empty
        self.assertIsNotNone(api_key)
    
    def test_create_key_with_special_characters(self):
        """Test creating key with special characters in name."""
        api_key, key_info = create_api_key('user123', 'Test Key <>&"\'')
        self.assertIsNotNone(api_key)
        self.assertEqual(key_info['key_name'], 'Test Key <>&"\'')
    
    def test_validate_with_whitespace(self):
        """Test validation with whitespace in key."""
        api_key, _ = create_api_key('user123', 'Test')
        
        # Add whitespace
        result = validate_api_key(f" {api_key} ")
        self.assertIsNone(result)  # Should fail with whitespace
    
    def test_list_keys_ordered_by_date(self):
        """Test that keys are listed in reverse chronological order."""
        create_api_key('user123', 'Key 1')
        time.sleep(0.1)
        create_api_key('user123', 'Key 2')
        time.sleep(0.1)
        create_api_key('user123', 'Key 3')
        
        keys = list_user_api_keys('user123')
        
        # Most recent should be first
        self.assertEqual(keys[0]['key_name'], 'Key 3')
        self.assertEqual(keys[1]['key_name'], 'Key 2')
        self.assertEqual(keys[2]['key_name'], 'Key 1')


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
