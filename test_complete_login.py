#!/usr/bin/env python3
"""Complete login test with proper URL handling"""
import requests

print("="*60)
print("COMPLETE LOGIN TEST")
print("="*60)

# Create a session to maintain cookies
session = requests.Session()

# Step 1: Load login page
print("\n1️⃣ Loading login page...")
response = session.get('http://127.0.0.1:5000/login')
print(f"   Status: {response.status_code}")

# Step 2: Submit login credentials
print("\n2️⃣ Submitting admin login (admin/admin123)...")
response = session.post('http://127.0.0.1:5000/login', data={
    'username': 'admin',
    'password': 'admin123'
})
print(f"   Status: {response.status_code}")

# Step 3: Try to access admin dashboard
print("\n3️⃣ Accessing admin dashboard...")
response = session.get('http://127.0.0.1:5000/admin/dashboard')
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    print("   ✓ Admin dashboard loaded successfully!")
    
    # Check for specific content
    if 'dashboard' in response.text.lower() or 'Ադմինիստրատոր' in response.text:
        print("   ✓ Page contains admin content")
    else:
        print("   ? Page loaded but content is unclear")
        
elif response.status_code == 302:
    print("   → Redirecting...")
    next_url = response.headers.get('Location', '')
    print(f"   → {next_url}")
    response = session.get(f'http://127.0.0.1:5000{next_url}')
    print(f"   Final status: {response.status_code}")
    
elif response.status_code == 401:
    print("   ✗ Not authenticated (401)")
    print("   → Session/cookies may not be working properly")
    
else:
    print(f"   ✗ Unexpected status: {response.status_code}")

# Step 4: Test user login as well
print("\n4️⃣ Testing regular user login...")
# First create a test user
from app import app, db, User

with app.app_context():
    test_user = User.query.filter_by(username='testuser').first()
    if not test_user:
        test_user = User(
            username='testuser',
            email='test@museum.am',
            role='user'
        )
        test_user.set_password('test1234')
        db.session.add(test_user)
        db.session.commit()
        print("   ✓ Test user created")
    else:
        print("   ✓ Test user already exists")

# Try logging in as test user
session2 = requests.Session()
response = session2.post('http://127.0.0.1:5000/login', data={
    'username': 'testuser',
    'password': 'test1234'
})
print(f"   Status: {response.status_code}")

# Try to access user dashboard
response = session2.get('http://127.0.0.1:5000/user/dashboard')
print(f"   User dashboard status: {response.status_code}")

print("\n" + "="*60)
print("✅ Login test complete")
print("="*60)
print("\nRECOMMENDATION:")
print("Try logging in at http://127.0.0.1:5000/login with:")
print("  • Username: admin")
print("  • Password: admin123")
print("  • Select the 'Ադմին' (Admin) tab")
