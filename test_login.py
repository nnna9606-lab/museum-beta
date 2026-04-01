#!/usr/bin/env python3
"""Test login functionality"""
from app import app, db, User
import requests

# Start by checking the admin account
print("="*60)
print("TEST 1: Check admin account in database")
print("="*60)

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"✓ Admin user exists")
        print(f"  Username: {admin.username}")
        print(f"  Email: {admin.email}")
        print(f"  Is admin: {admin.is_admin}")
        print(f"  Is active: {admin.is_active}")
        
        # Test password verification
        is_valid = admin.check_password('admin123')
        print(f"  Password 'admin123' is valid: {is_valid}")
        
        if not is_valid:
            print("\n⚠️  Password doesn't match. Resetting to 'admin123'...")
            admin.set_password('admin123')
            db.session.commit()
            print("✓ Password reset")
    else:
        print("✗ Admin user not found!")
        print("\nCreating admin user...")
        admin = User(
            username='admin',
            email='admin@museum.am',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created")

# Test login via HTTP
print("\n" + "="*60)
print("TEST 2: Test login via HTTP request")
print("="*60)

try:
    # First, test GET request to login page
    response = requests.get('http://127.0.0.1:5000/login')
    print(f"GET /login: {response.status_code}")
    if response.status_code == 200:
        print("✓ Login page loads")
    else:
        print(f"✗ Error loading login page")
    
    # Test POST request with admin credentials
    print("\nTesting login with admin/admin123...")
    session = requests.Session()
    
    response = session.post('http://127.0.0.1:5000/login', data={
        'username': 'admin',
        'password': 'admin123',
        'remember': 'on'
    }, allow_redirects=False)
    
    print(f"POST /login: {response.status_code}")
    
    if response.status_code == 302:
        print(f"✓ Redirect received (302)")
        next_url = response.headers.get('Location', '')
        print(f"  Redirecting to: {next_url}")
        
        # Try to follow the redirect
        final_response = session.get(next_url)
        print(f"  Final page: {final_response.status_code}")
        
    elif response.status_code == 200:
        # Check if there's a flash message
        if 'Սխալ' in response.text or 'error' in response.text.lower():
            print("✗ Login failed - error message present")
            # extract error message
            import re
            match = re.search(r'<div class="flash-item">([^<]+)</div>', response.text)
            if match:
                print(f"  Error: {match.group(1)}")
        else:
            print("? Unexpected response")
    else:
        print(f"✗ Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"✗ Connection error: {e}")
    print("  Make sure Flask server is running on http://127.0.0.1:5000")

print("\n" + "="*60)
print("✅ Test complete")
print("="*60)
