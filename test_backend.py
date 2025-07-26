#!/usr/bin/env python3
"""
Backend API Testing Script for GlobalTrade AI
Tests all major API endpoints and functionality
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
            print(f"   Features: {', '.join([k for k, v in data['features'].items() if v])}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n🔍 Testing user registration...")
    try:
        user_data = {
            "full_name": "Test User",
            "email": "test@globaltrade.ai",
            "password": "test123",
            "country": "ID",
            "language": "en",
            "company_name": "Test Coffee Co",
            "phone": "+62123456789"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ User registration successful: {data['user']['full_name']}")
            return data['access_token']
        else:
            print(f"❌ User registration failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return None

def test_user_login():
    """Test user login"""
    print("\n🔍 Testing user login...")
    try:
        login_data = {
            "email": "test@globaltrade.ai",
            "password": "test123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User login successful: {data['user']['full_name']}")
            return data['access_token']
        else:
            print(f"❌ User login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ User login error: {e}")
        return None

def test_protected_endpoints(token):
    """Test protected endpoints"""
    print("\n🔍 Testing protected endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("/users/profile", "GET", "User profile"),
        ("/chat/conversations", "GET", "Chat conversations"),
        ("/market/research", "GET", "Market research"),
        ("/products", "GET", "Products list"),
        ("/media/files", "GET", "Media files"),
        ("/media/social/platforms", "GET", "Social platforms")
    ]
    
    success_count = 0
    for endpoint, method, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers)
                
            if response.status_code in [200, 201]:
                print(f"✅ {description}: OK")
                success_count += 1
            else:
                print(f"❌ {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    print(f"\n📊 Protected endpoints: {success_count}/{len(endpoints)} passed")
    return success_count == len(endpoints)

def test_ai_agents(token):
    """Test AI agent functionality"""
    print("\n🔍 Testing AI agents...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test translation
    try:
        translation_data = {
            "text": "Hello, I want to buy coffee",
            "target_language": "id",
            "context": "business"
        }
        
        response = requests.post(f"{BASE_URL}/chat/translate", 
                               json=translation_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Translation service: '{data['translated_text']}'")
        else:
            print(f"❌ Translation service: {response.status_code}")
    except Exception as e:
        print(f"❌ Translation service error: {e}")
    
    # Test market research
    try:
        research_data = {
            "product": "coffee",
            "target_country": "IT",
            "analysis_type": "market_overview"
        }
        
        response = requests.post(f"{BASE_URL}/market/research", 
                               json=research_data, headers=headers)
        if response.status_code == 200:
            print("✅ Market research service: OK")
        else:
            print(f"❌ Market research service: {response.status_code}")
    except Exception as e:
        print(f"❌ Market research service error: {e}")

def run_tests():
    """Run all tests"""
    print("🚀 Starting GlobalTrade AI Backend Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Backend is not running or unhealthy")
        return False
    
    # Test 2: User registration
    token = test_user_registration()
    if not token:
        # Try login instead
        token = test_user_login()
        if not token:
            print("\n❌ Authentication failed")
            return False
    
    # Test 3: Protected endpoints
    test_protected_endpoints(token)
    
    # Test 4: AI agents
    test_ai_agents(token)
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")
    return True

if __name__ == "__main__":
    print("GlobalTrade AI Backend Test Suite")
    print("Make sure the Flask backend is running on localhost:5000")
    print()
    
    # Wait a moment for user to start backend if needed
    input("Press Enter to start testing (or Ctrl+C to cancel)...")
    
    success = run_tests()
    sys.exit(0 if success else 1)

