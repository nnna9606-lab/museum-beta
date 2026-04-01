#!/usr/bin/env python3
"""Debug admin login issue with detailed logging"""
from app import app, db, User
from flask import session

print("\n" + "="*70)
print("🔍 COMPLETE ADMIN LOGIN DEBUGGING")
print("="*70)

# Check 1: Database user
print("\n[1] Database Check")
print("-" * 70)
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"✓ Username: {admin.username}")
        print(f"✓ Email: {admin.email}")
        print(f"✓ Role: {admin.role}")
        print(f"✓ Is Admin: {admin.is_admin}")
        print(f"✓ Is Active: {admin.is_active}")
        
        # Password check
        pwd_valid = admin.check_password('admin123')
        print(f"✓ Password valid: {pwd_valid}")
        
        if not pwd_valid:
            print("\n⚠️  Password check failed! Resetting...")
            admin.set_password('admin123')
            db.session.commit()
            print("✓ Password reset successfully")
    else:
        print("✗ No admin user found")

# Check 2: Test login context
print("\n[2] Testing Login Context")
print("-" * 70)

with app.test_client() as client:
    # Test GET request to login page
    print("GET /login:")
    response = client.get('/login')
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  ✓ Login page accessible")
        
        # Check if translation context is available
        response_text = response.data.decode('utf-8', errors='ignore')
        if 'admin' in response_text.lower():
            print("  ✓ Admin login tab present")
    
    # Test POST with admin credentials
    print("\nPOST /login (admin/admin123):")
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123',
        'remember': 'on'
    }, follow_redirects=False)
    
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 302:
        print(f"  ✓ Redirect: {response.location}")
        
        # Follow redirect
        print("\nFollowing redirect...")
        response = client.get(response.location)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✓ Admin dashboard accessible after login")
        else:
            print(f"  ✗ Could not access admin dashboard")
    
    elif response.status_code == 200:
        # Check for error message
        response_text = response.data.decode('utf-8', errors='ignore')
        if 'Սխալ' in response_text or 'error' in response_text.lower():
            print("  ✗ Login returned error")
            # Try to extract error
            if 'Սխալ օգտանուն' in response_text:
                print("  Error: Invalid username or password")
        else:
            print("  ? Unexpected response (no redirect, no error)")
    
    else:
        print(f"  ✗ Unexpected status: {response.status_code}")

# Check 3: Test with different passwords
print("\n[3] Testing Various Passwords")
print("-" * 70)

test_passwords = ['admin123', 'admin', '123456', 'password']

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    for pwd in test_passwords:
        result = admin.check_password(pwd)
        status = "✓" if result else "✗"
        print(f"  {status} '{pwd}': {result}")

# Check 4: Login instructions
print("\n[4] Login Instructions for Manual Testing")
print("-" * 70)
print("""
To log in as admin:

1. Go to: http://127.0.0.1:5000/login
2. Click the "Ադմին" (Admin) tab on the right
3. Enter credentials:
   - Username: admin
   - Password: admin123
4. Click "Ադմինի մուտք" (Admin Login) button

Alternative: Use the regular "Օգտատեր" (User) tab with same credentials
since admin accounts can also log in as regular users.

If you still can't log in:
- Check browser console for JavaScript errors
- Clear browser cookies and cache
- Try a different browser
- Check if Flask server is running (port 5000)
""")

print("\n" + "="*70)
print("✅ Debugging complete")
print("="*70)
