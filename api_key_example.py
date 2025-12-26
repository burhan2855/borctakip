"""
Example usage of the API Key Management System.
Demonstrates how to create, validate, list, and revoke API keys.
"""

import sys
from api_key_manager import (
    create_api_key,
    validate_api_key,
    list_user_api_keys,
    revoke_api_key,
    delete_api_key,
    get_api_key_info
)
from api_auth_middleware import authenticate_api_request
from init_api_keys_db import init_api_keys_table


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def example_create_api_key():
    """Example: Create a new API key."""
    print_section("1. Creating API Keys")
    
    # Create a live API key
    api_key, key_info = create_api_key(
        user_id="user123",
        key_name="Mobil Uygulama",
        key_type="live"
    )
    
    if api_key and key_info:
        print(f"\n✓ Live API Key Created Successfully!")
        print(f"\n  API Key: {api_key}")
        print(f"  Key Name: {key_info['key_name']}")
        print(f"  Key Prefix: {key_info['key_prefix']}")
        print(f"  Created: {key_info['created_at']}")
        print(f"\n  ⚠️  IMPORTANT: Save this key securely!")
        print(f"  ⚠️  You won't be able to see it again!")
        print(f"\n  This key can be used in API requests:")
        print(f"  Authorization: Bearer {api_key}")
        return api_key, key_info
    else:
        print("✗ Failed to create API key")
        return None, None


def example_create_test_key():
    """Example: Create a test API key."""
    print("\n" + "-" * 60)
    
    # Create a test API key with expiration
    api_key, key_info = create_api_key(
        user_id="user123",
        key_name="Test Environment",
        key_type="test",
        expires_days=30
    )
    
    if api_key and key_info:
        print(f"\n✓ Test API Key Created Successfully!")
        print(f"\n  API Key: {api_key}")
        print(f"  Key Name: {key_info['key_name']}")
        print(f"  Key Prefix: {key_info['key_prefix']}")
        print(f"  Expires: {key_info['expires_at']}")
        return api_key, key_info
    else:
        print("✗ Failed to create test API key")
        return None, None


def example_validate_api_key(api_key):
    """Example: Validate an API key."""
    print_section("2. Validating API Key")
    
    key_data = validate_api_key(api_key)
    
    if key_data:
        print(f"\n✓ API Key is VALID!")
        print(f"\n  User ID: {key_data['user_id']}")
        print(f"  Key Name: {key_data['key_name']}")
        print(f"  Last Used: {key_data['last_used_at']}")
        print(f"  Active: {key_data['is_active']}")
    else:
        print("\n✗ API Key is INVALID or EXPIRED")
    
    return key_data


def example_authenticate_request(api_key):
    """Example: Authenticate a request using middleware."""
    print_section("3. Authenticating API Request")
    
    # Simulate an HTTP Authorization header
    auth_header = f"Bearer {api_key}"
    print(f"\n  Authorization Header: {auth_header[:30]}...")
    
    auth_context = authenticate_api_request(auth_header)
    
    if auth_context:
        print(f"\n✓ Request Authenticated!")
        print(f"\n  User ID: {auth_context['user_id']}")
        print(f"  Key Name: {auth_context['key_name']}")
        print(f"  Authenticated: {auth_context['authenticated']}")
    else:
        print("\n✗ Authentication Failed!")
    
    return auth_context


def example_list_api_keys():
    """Example: List all API keys for a user."""
    print_section("4. Listing User's API Keys")
    
    keys = list_user_api_keys("user123")
    
    if keys:
        print(f"\n  Found {len(keys)} API key(s):\n")
        for i, key in enumerate(keys, 1):
            status = "🟢 Active" if key['is_active'] else "🔴 Inactive"
            print(f"  {i}. {key['key_name']}")
            print(f"     ID: {key['id']}")
            print(f"     Prefix: {key['key_prefix']}")
            print(f"     Status: {status}")
            print(f"     Created: {key['created_at']}")
            if key['last_used_at']:
                print(f"     Last Used: {key['last_used_at']}")
            if key['expires_at']:
                print(f"     Expires: {key['expires_at']}")
            print()
    else:
        print("\n  No API keys found for this user.")
    
    return keys


def example_revoke_api_key(key_id):
    """Example: Revoke an API key."""
    print_section("5. Revoking API Key")
    
    print(f"\n  Revoking key ID: {key_id}")
    
    success = revoke_api_key(key_id, "user123")
    
    if success:
        print(f"\n✓ API Key revoked successfully!")
        print(f"  The key is now inactive and cannot be used.")
    else:
        print("\n✗ Failed to revoke API key")
    
    return success


def example_verify_revoked_key(api_key):
    """Example: Try to validate a revoked key."""
    print_section("6. Verifying Revoked Key")
    
    print(f"\n  Attempting to validate revoked key...")
    
    key_data = validate_api_key(api_key)
    
    if key_data:
        print(f"\n  ⚠️  WARNING: Revoked key is still valid!")
    else:
        print(f"\n✓ Correctly rejected! Revoked key cannot be used.")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("  API KEY MANAGEMENT SYSTEM - EXAMPLE USAGE")
    print("=" * 60)
    print("\n  This script demonstrates the complete API key lifecycle:")
    print("    • Creating API keys")
    print("    • Validating API keys")
    print("    • Authenticating requests")
    print("    • Listing keys")
    print("    • Revoking keys")
    
    # Initialize database
    print("\n  Initializing database...")
    init_api_keys_table('debt_database')
    
    # Create API keys
    live_key, live_info = example_create_api_key()
    if not live_key:
        print("\n✗ Could not proceed without a valid API key")
        return
    
    test_key, test_info = example_create_test_key()
    
    # Validate API key
    example_validate_api_key(live_key)
    
    # Authenticate request
    example_authenticate_request(live_key)
    
    # List API keys
    keys = example_list_api_keys()
    
    # Revoke the first key
    if live_info:
        example_revoke_api_key(live_info['id'])
        
        # Verify revoked key doesn't work
        example_verify_revoked_key(live_key)
        
        # List keys again to see the change
        print_section("7. Updated API Keys List")
        example_list_api_keys()
    
    # Security best practices
    print_section("Security Best Practices")
    print("""
  ✓ API keys are hashed in the database (SHA-256)
  ✓ Keys are only shown once during creation
  ✓ Last usage timestamps are tracked
  ✓ Keys can be revoked at any time
  ✓ Optional expiration dates are supported
  ✓ Use HTTPS in production
  ✓ Never log API keys
  ✓ Implement rate limiting for production
    """)
    
    print("\n" + "=" * 60)
    print("  Example completed successfully!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
