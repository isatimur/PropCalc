#!/usr/bin/env python3
"""
Test script to debug authentication issues
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment variables
os.environ['SECRET_KEY'] = 'test_secret_key_for_development_only_change_in_production_12345'
os.environ['ENVIRONMENT'] = 'development'
os.environ['LOG_LEVEL'] = 'INFO'

try:
    from propcalc.api.auth import router
    print("✅ Auth router imported successfully")
    
    # Test the login function directly
    from propcalc.api.auth import login
    print("✅ Login function imported successfully")
    
    # Test JWT manager
    from propcalc.core.security.jwt_manager import jwt_manager, password_manager
    print("✅ JWT manager imported successfully")
    
    # Test creating a token
    token_data = {
        "sub": "1",
        "username": "admin",
        "email": "admin@propcalc.com",
        "role": "admin",
        "permissions": ["read", "write", "admin"]
    }
    
    access_token = jwt_manager.create_access_token(token_data)
    print(f"✅ Access token created successfully: {access_token[:50]}...")
    
    print("\n🎉 All authentication components working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
