from app import app, db, User

USERNAME = 'testuser'
PASSWORD = 'testpass'
EMAIL = 'testuser@example.com'

with app.app_context():
    user = User.query.filter_by(username=USERNAME).first()
    if not user:
        user = User(username=USERNAME, email=EMAIL)
        user.set_password(PASSWORD)
        db.session.add(user)
        db.session.commit()
        print('Created test user')
    else:
        # Ensure password is correct for the test
        user.set_password(PASSWORD)
        db.session.commit()
        print('Ensured test user password')

# Use Flask test client to log in and fetch the settings page
with app.test_client() as c:
    login_resp = c.post('/login', data={'username': USERNAME, 'password': PASSWORD}, follow_redirects=True)
    print('Login status code:', login_resp.status_code)
    # check for Armenian failure message (encoded)
    if 'Սխալ օգտանուն կամ գաղտնաբառ' in login_resp.get_data(as_text=True):
        print('Login failed (invalid credentials)')
    settings_resp = c.get('/user/settings')
    print('Settings status code:', settings_resp.status_code)
    data = settings_resp.get_data(as_text=True)
    print('Settings page length:', len(data))
    # Quick check for key heading
    found = 'Կարգավորումներ' in data
    print('Contains "Կարգավորումներ" heading:', found)
