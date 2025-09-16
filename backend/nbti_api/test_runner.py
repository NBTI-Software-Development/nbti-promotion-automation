#!/usr/bin/env python3
"""
Simple test runner for the NBTI Promotion Automation API
"""

import os
import sys
import requests
import time
import subprocess
import signal
from threading import Thread

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def start_test_server():
    """Start the Flask server for testing."""
    print("Starting test server...")
    env = os.environ.copy()
    env['FLASK_ENV'] = 'testing'
    env['DATABASE_URL'] = 'sqlite:///test.db'
    
    process = subprocess.Popen([
        sys.executable, 'src/main.py'
    ], env=env, cwd=os.path.dirname(__file__))
    
    # Wait for server to start
    time.sleep(3)
    
    return process

def test_api_endpoints():
    """Test API endpoints manually."""
    base_url = "http://localhost:5000"
    
    tests_passed = 0
    tests_failed = 0
    
    print("\n=== API Endpoint Tests ===")
    
    # Test 1: Health check (if it exists)
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            tests_passed += 1
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            tests_failed += 1
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Health endpoint not available (expected): {e}")
    
    # Test 2: User registration
    try:
        user_data = {
            "username": "testuser123",
            "email": "test123@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/api/auth/register", json=user_data, timeout=5)
        if response.status_code == 201:
            print("✅ User registration working")
            tests_passed += 1
        else:
            print(f"❌ User registration failed: {response.status_code} - {response.text}")
            tests_failed += 1
    except requests.exceptions.RequestException as e:
        print(f"❌ User registration error: {e}")
        tests_failed += 1
    
    # Test 3: User login
    try:
        login_data = {
            "username": "testuser123",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            print("✅ User login working")
            tests_passed += 1
            
            # Get token for authenticated tests
            token = response.json().get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test 4: Get current user
            try:
                response = requests.get(f"{base_url}/api/auth/me", headers=headers, timeout=5)
                if response.status_code == 200:
                    print("✅ Get current user working")
                    tests_passed += 1
                else:
                    print(f"❌ Get current user failed: {response.status_code}")
                    tests_failed += 1
            except requests.exceptions.RequestException as e:
                print(f"❌ Get current user error: {e}")
                tests_failed += 1
            
            # Test 5: PMS Dashboard
            try:
                response = requests.get(f"{base_url}/api/pms/dashboard", headers=headers, timeout=5)
                if response.status_code == 200:
                    print("✅ PMS dashboard working")
                    tests_passed += 1
                else:
                    print(f"❌ PMS dashboard failed: {response.status_code}")
                    tests_failed += 1
            except requests.exceptions.RequestException as e:
                print(f"❌ PMS dashboard error: {e}")
                tests_failed += 1
            
            # Test 6: EMM Dashboard
            try:
                response = requests.get(f"{base_url}/api/emm/dashboard", headers=headers, timeout=5)
                if response.status_code == 200:
                    print("✅ EMM dashboard working")
                    tests_passed += 1
                else:
                    print(f"❌ EMM dashboard failed: {response.status_code}")
                    tests_failed += 1
            except requests.exceptions.RequestException as e:
                print(f"❌ EMM dashboard error: {e}")
                tests_failed += 1
                
        else:
            print(f"❌ User login failed: {response.status_code} - {response.text}")
            tests_failed += 1
    except requests.exceptions.RequestException as e:
        print(f"❌ User login error: {e}")
        tests_failed += 1
    
    print(f"\n=== Test Results ===")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"📊 Total: {tests_passed + tests_failed}")
    
    return tests_passed, tests_failed

def test_code_quality():
    """Test code quality with basic checks."""
    print("\n=== Code Quality Tests ===")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Check if all Python files can be imported
    try:
        import models.user
        import models.pms
        import models.emm
        import routes.auth
        import routes.user
        import routes.pms
        import routes.emm
        print("✅ All modules can be imported")
        tests_passed += 1
    except ImportError as e:
        print(f"❌ Import error: {e}")
        tests_failed += 1
    
    # Test 2: Check for basic syntax errors with flake8 (if available)
    try:
        result = subprocess.run(['flake8', 'src/', '--count', '--select=E9,F63,F7,F82', '--show-source', '--statistics'], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        if result.returncode == 0:
            print("✅ No critical syntax errors found")
            tests_passed += 1
        else:
            print(f"❌ Syntax errors found:\n{result.stdout}")
            tests_failed += 1
    except FileNotFoundError:
        print("⚠️  flake8 not available, skipping syntax check")
    
    print(f"\n=== Code Quality Results ===")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    
    return tests_passed, tests_failed

def main():
    """Main test runner."""
    print("🚀 NBTI Promotion Automation - Test Suite")
    print("=" * 50)
    
    # Start server
    server_process = None
    try:
        server_process = start_test_server()
        
        # Run tests
        api_passed, api_failed = test_api_endpoints()
        quality_passed, quality_failed = test_code_quality()
        
        total_passed = api_passed + quality_passed
        total_failed = api_failed + quality_failed
        
        print(f"\n🎯 FINAL RESULTS")
        print("=" * 50)
        print(f"✅ Total Passed: {total_passed}")
        print(f"❌ Total Failed: {total_failed}")
        print(f"📊 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
        
        if total_failed == 0:
            print("\n🎉 All tests passed! The system is working correctly.")
            return 0
        else:
            print(f"\n⚠️  {total_failed} tests failed. Please review the issues above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        return 1
    finally:
        # Clean up server
        if server_process:
            print("\n🛑 Stopping test server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

if __name__ == "__main__":
    sys.exit(main())

