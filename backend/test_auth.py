#!/usr/bin/env python3
"""
Simple test script for the authentication system
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "testpass123",
    "role": "viewer"
}

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=TEST_USER
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Registration successful")
        else:
            print("❌ Registration failed")
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    try:
        # Try with test user first
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        
        print(f"Test User Login - Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Try with admin user
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        print(f"Admin Login - Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error during login: {e}")

def test_invalid_login():
    """Test invalid login attempts"""
    print("\nTesting invalid login...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "username": "invalid",
                "password": "wrongpassword"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Invalid login properly rejected")
        else:
            print("❌ Invalid login not properly handled")
            
    except Exception as e:
        print(f"❌ Error during invalid login test: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Authentication System Tests")
    print("=" * 50)
    
    # Test registration
    test_register()
    
    # Test login
    test_login()
    
    # Test invalid login
    test_invalid_login()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed")

if __name__ == "__main__":
    main()
