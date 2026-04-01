from app import app, db, User, Artifact, Exhibition
from werkzeug.security import generate_password_hash

TEST_USER = 'testuser'
TEST_PASS = 'password123'

with app.app_context():
    db.create_all()
    user = User.query.filter_by(username=TEST_USER).first()
    if not user:
        user = User(username=TEST_USER, email='test@example.com', role='user')
        user.set_password(TEST_PASS)
        db.session.add(user)
        db.session.commit()
    # ensure there is at least one artifact and one exhibition
    art = Artifact.query.first()
    if not art:
        art = Artifact(name='Sample Artifact', description='Sample', year=1900)
        db.session.add(art)
        db.session.commit()
    ex = Exhibition.query.first()
    if not ex:
        ex = Exhibition(title='Sample Exhibition', description='Demo', start_date='2025-01-01', end_date='2025-12-31')
        # SQLAlchemy will coerce strings to date? If not, set with date object
        from datetime import date
        ex.start_date = date(2025,1,1)
        ex.end_date = date(2025,12,31)
        db.session.add(ex)
        db.session.commit()

    client = app.test_client()
    # login by setting session user id (bypass form auth for test client)
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
    print('Session set for user id:', user.id)

    # favorite artifact
    aid = art.id
    r = client.post(f'/favorite/artifact/{aid}')
    print('Favorite artifact response:', r.status_code, r.get_data(as_text=True))
    # toggle again
    r2 = client.post(f'/favorite/artifact/{aid}')
    print('Toggle artifact response:', r2.status_code, r2.get_data(as_text=True))

    # favorite exhibition
    eid = ex.id
    r3 = client.post(f'/favorite/exhibition/{eid}')
    print('Favorite exhibition response:', r3.status_code, r3.get_data(as_text=True))
    r4 = client.post(f'/favorite/exhibition/{eid}')
    print('Toggle exhibition response:', r4.status_code, r4.get_data(as_text=True))

    # fetch favorites page
    fav = client.get('/favorites')
    print('Favorites page status:', fav.status_code)
    print(fav.get_data(as_text=True)[:800])
