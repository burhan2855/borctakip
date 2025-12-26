"""
Verification script to confirm all requirements are met.
This script tests that the API key management system meets all specified requirements.
"""

import sys
import sqlite3
from datetime import datetime, timezone

def check_database_schema():
    """Verify database schema matches requirements."""
    print("=" * 60)
    print("1. Checking Database Schema")
    print("=" * 60)
    
    conn = sqlite3.connect('debt_database')
    cursor = conn.cursor()
    
    # Check if api_keys table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys'")
    if not cursor.fetchone():
        print("❌ api_keys table not found")
        return False
    
    # Check table structure
    cursor.execute("PRAGMA table_info(api_keys)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    required_columns = {
        'id': 'INTEGER',
        'user_id': 'TEXT',
        'key_name': 'TEXT',
        'api_key': 'TEXT',
        'key_prefix': 'TEXT',
        'created_at': 'TEXT',
        'last_used_at': 'TEXT',
        'is_active': 'INTEGER',
        'expires_at': 'TEXT'
    }
    
    for col, col_type in required_columns.items():
        if col not in columns:
            print(f"❌ Column '{col}' not found")
            return False
        if not columns[col].startswith(col_type):
            print(f"❌ Column '{col}' has wrong type: {columns[col]} (expected {col_type})")
            return False
    
    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='api_keys'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    required_indexes = ['idx_api_keys_user_id', 'idx_api_keys_api_key', 'idx_api_keys_is_active']
    for idx in required_indexes:
        if idx not in indexes:
            print(f"❌ Index '{idx}' not found")
            return False
    
    conn.close()
    print("✅ Database schema is correct")
    print("✅ All required columns present")
    print("✅ All indexes created")
    return True

def check_api_key_generation():
    """Verify API key generation meets requirements."""
    print("\n" + "=" * 60)
    print("2. Checking API Key Generation & Security")
    print("=" * 60)
    
    from api_key_manager import create_api_key, _hash_api_key
    
    # Create a test key
    api_key, key_info = create_api_key('test_user', 'Test Key', key_type='live')
    
    if not api_key or not key_info:
        print("❌ Failed to create API key")
        return False
    
    # Check key length
    if len(api_key) < 32:
        print(f"❌ API key too short: {len(api_key)} characters (minimum 32)")
        return False
    
    # Check prefix
    if not api_key.startswith('sk_live_'):
        print(f"❌ API key doesn't start with 'sk_live_': {api_key[:12]}")
        return False
    
    # Verify hashing
    hashed = _hash_api_key(api_key)
    if len(hashed) != 64:  # SHA-256 produces 64 hex characters
        print(f"❌ Hash length incorrect: {len(hashed)} (expected 64)")
        return False
    
    # Verify key is not stored in plaintext
    conn = sqlite3.connect('debt_database')
    cursor = conn.cursor()
    cursor.execute('SELECT api_key FROM api_keys WHERE id = ?', (key_info['id'],))
    stored_key = cursor.fetchone()[0]
    conn.close()
    
    if stored_key == api_key:
        print("❌ API key stored in plaintext!")
        return False
    
    if stored_key != hashed:
        print("❌ Stored key doesn't match hash")
        return False
    
    # Test test key prefix
    test_key, test_info = create_api_key('test_user', 'Test Env', key_type='test')
    if not test_key.startswith('sk_test_'):
        print(f"❌ Test key doesn't start with 'sk_test_': {test_key[:12]}")
        return False
    
    print(f"✅ API keys are secure (32+ characters)")
    print(f"✅ Keys use correct prefixes (sk_live_ and sk_test_)")
    print(f"✅ Keys are hashed with SHA-256")
    print(f"✅ Keys are NOT stored in plaintext")
    return True

def check_api_key_management():
    """Verify all API key management functions work."""
    print("\n" + "=" * 60)
    print("3. Checking API Key Management Functions")
    print("=" * 60)
    
    from api_key_manager import (
        create_api_key, validate_api_key, list_user_api_keys,
        revoke_api_key, delete_api_key
    )
    
    # Test create
    api_key, key_info = create_api_key('verify_user', 'Verify Key')
    if not api_key or not key_info:
        print("❌ create_api_key failed")
        return False
    print("✅ create_api_key works")
    
    # Test validate
    validated = validate_api_key(api_key)
    if not validated or validated['user_id'] != 'verify_user':
        print("❌ validate_api_key failed")
        return False
    print("✅ validate_api_key works")
    
    # Test list
    keys = list_user_api_keys('verify_user')
    if len(keys) != 1 or keys[0]['key_name'] != 'Verify Key':
        print("❌ list_user_api_keys failed")
        return False
    print("✅ list_user_api_keys works")
    
    # Test revoke
    if not revoke_api_key(key_info['id'], 'verify_user'):
        print("❌ revoke_api_key failed")
        return False
    
    # Verify revoked key doesn't validate
    if validate_api_key(api_key) is not None:
        print("❌ Revoked key still validates")
        return False
    print("✅ revoke_api_key works")
    
    # Test delete
    if not delete_api_key(key_info['id'], 'verify_user'):
        print("❌ delete_api_key failed")
        return False
    
    keys = list_user_api_keys('verify_user')
    if len(keys) != 0:
        print("❌ Deleted key still in database")
        return False
    print("✅ delete_api_key works")
    
    return True

def check_authentication_middleware():
    """Verify authentication middleware works."""
    print("\n" + "=" * 60)
    print("4. Checking Authentication Middleware")
    print("=" * 60)
    
    from api_key_manager import create_api_key
    from api_auth_middleware import authenticate_api_request, check_api_auth
    
    # Create test key
    api_key, key_info = create_api_key('auth_test_user', 'Auth Test')
    
    # Test Bearer authentication
    auth_header = f"Bearer {api_key}"
    auth_context = authenticate_api_request(auth_header)
    
    if not auth_context:
        print("❌ authenticate_api_request failed")
        return False
    
    if auth_context['user_id'] != 'auth_test_user':
        print("❌ Wrong user_id in auth context")
        return False
    
    print("✅ Bearer token authentication works")
    
    # Test last_used_at update
    from api_key_manager import validate_api_key
    key_data = validate_api_key(api_key)
    if not key_data['last_used_at']:
        print("❌ last_used_at not updated")
        return False
    
    print("✅ last_used_at timestamp is updated")
    
    # Test invalid authentication
    invalid_result = authenticate_api_request("Bearer invalid_key")
    if invalid_result is not None:
        print("❌ Invalid key was authenticated")
        return False
    
    print("✅ Invalid keys are rejected")
    
    # Test check_api_auth
    is_auth, context = check_api_auth(auth_header)
    if not is_auth or not context:
        print("❌ check_api_auth failed")
        return False
    
    print("✅ check_api_auth helper works")
    
    return True

def check_key_features():
    """Verify additional key features."""
    print("\n" + "=" * 60)
    print("5. Checking Additional Features")
    print("=" * 60)
    
    from api_key_manager import create_api_key, validate_api_key
    
    # Test key shown only once
    api_key1, key_info1 = create_api_key('feature_user', 'Feature Test')
    
    # List keys - should show masked version
    from api_key_manager import list_user_api_keys
    keys = list_user_api_keys('feature_user')
    
    if api_key1 in str(keys):
        print("❌ Full API key visible in list")
        return False
    
    if not keys[0]['key_prefix'].endswith('...'):
        print("❌ Key prefix not masked")
        return False
    
    print("✅ Keys are masked in listings")
    
    # Test expiration
    expired_key, expired_info = create_api_key(
        'feature_user', 'Expired Key', expires_days=-1
    )
    
    if validate_api_key(expired_key) is not None:
        print("❌ Expired key still validates")
        return False
    
    print("✅ Expired keys are rejected")
    
    # Test that expiration is optional
    no_expire_key, no_expire_info = create_api_key('feature_user', 'No Expire')
    if no_expire_info['expires_at'] is not None:
        print("❌ Expiration was set when not requested")
        return False
    
    print("✅ Expiration is optional")
    
    return True

def check_documentation():
    """Verify documentation exists."""
    print("\n" + "=" * 60)
    print("6. Checking Documentation")
    print("=" * 60)
    
    import os
    
    required_files = [
        'api_key_manager.py',
        'api_auth_middleware.py',
        'init_api_keys_db.py',
        'api_key_example.py',
        'test_api_keys.py',
        'API_KEY_MANAGEMENT.md'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file not found: {file}")
            return False
        print(f"✅ {file} exists")
    
    # Check README
    with open('README.md', 'r') as f:
        readme = f.read()
        if 'API' not in readme and 'api' not in readme:
            print("❌ README not updated with API key info")
            return False
    
    print("✅ README updated")
    
    return True

def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("API KEY MANAGEMENT SYSTEM - REQUIREMENTS VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("Database Schema", check_database_schema),
        ("API Key Generation & Security", check_api_key_generation),
        ("API Key Management Functions", check_api_key_management),
        ("Authentication Middleware", check_authentication_middleware),
        ("Additional Features", check_key_features),
        ("Documentation", check_documentation)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL REQUIREMENTS MET!")
        print("=" * 60)
        print("\nThe API Key Management System is complete and working:")
        print("  ✅ Secure key generation (32+ characters)")
        print("  ✅ SHA-256 hashing")
        print("  ✅ Proper key prefixes (sk_live_ / sk_test_)")
        print("  ✅ Keys shown only once")
        print("  ✅ Full CRUD operations")
        print("  ✅ Bearer token authentication")
        print("  ✅ Last usage tracking")
        print("  ✅ Optional expiration")
        print("  ✅ Comprehensive tests")
        print("  ✅ Full documentation")
        return 0
    else:
        print("⚠️  SOME REQUIREMENTS NOT MET")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
