from app import app, db, User
from io import BytesIO
from PIL import Image

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
        user.set_password(PASSWORD)
        db.session.commit()
        print('Ensured test user')

with app.test_client() as c:
    # login
    login = c.post('/login', data={'username': USERNAME, 'password': PASSWORD}, follow_redirects=True)
    print('Login status:', login.status_code)

    # Try to change password WITHOUT current password -> should fail
    resp1 = c.post('/user/settings', data={'password': 'newpass'}, follow_redirects=True)
    print('Change without current status:', resp1.status_code)
    print('Contains error (current password required):', 'Խնդրում ենք մուտքագրել ձեր ընթացիկ գաղտնաբառը' in resp1.get_data(as_text=True))

    # Change password WITH current password -> should succeed
    resp2 = c.post('/user/settings', data={'password': 'newpass', 'current_password': PASSWORD}, follow_redirects=True)
    print('Change with current status:', resp2.status_code)
    print('Contains success:', 'Ձեր կարգավորումները հաջողությամբ թարմացվել են' in resp2.get_data(as_text=True))

    # Re-login with new password
    logout = c.get('/logout', follow_redirects=True)
    login2 = c.post('/login', data={'username': USERNAME, 'password': 'newpass'}, follow_redirects=True)
    print('Re-login with new password status:', login2.status_code)
    print('Re-login success (redirected to dashboard):', login2.status_code == 200)

    # Upload a small PNG as profile image (create valid 1x1 PNG)
    img = BytesIO()
    im = Image.new('RGBA', (1,1), (255,0,0,255))
    im.save(img, format='PNG')
    img.seek(0)
    data = {
        'current_password': 'newpass',
        'username': USERNAME,
        'email': EMAIL,
        'profile_image': (img, 'test.png')
    }
    resp3 = c.post('/user/settings', data=data, content_type='multipart/form-data', follow_redirects=True)
    print('Profile image upload status:', resp3.status_code)
    print('Profile image saved:', 'Ձեր կարգավորումները հաջողությամբ թարմացվել են' in resp3.get_data(as_text=True))

    # Verify in DB
    with app.app_context():
        u = User.query.filter_by(username=USERNAME).first()
        print('DB profile_image:', bool(u.profile_image))
