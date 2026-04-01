from app import app, db, User, Artifact, Exhibition
from datetime import datetime, timedelta

# Ստեղծում ենք բոլոր աղյուսակները
with app.app_context():
    db.drop_all()  # Ջնջում ենք հին աղյուսակները
    db.create_all()  # Ստեղծում ենք նոր աղյուսակները
    
    # Ստեղծում ենք ադմին օգտատեր
    admin = User(
        username='admin',
        email='admin@museum.am',
        role='admin',
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Ստեղծում ենք թեստային օգտատեր
    user = User(
        username='user',
        email='user@example.com',
        role='user',
        is_active=True
    )
    user.set_password('user123')
    db.session.add(user)
    
    db.session.commit()
    
    # Ստեղծում ենք մի քանի նմուշ
    artifacts = [
        Artifact(
            name='Հին հայկական խեցեղեն',
            description='5-րդ դարի հայկական խեցեղեն՝ գտնված Արմավիրի պեղումների ժամանակ',
            year=450,
            image_url='https://example.com/ceramic.jpg',
            user_id=1
        ),
        Artifact(
            name='Արծաթե զարդեր',
            description='Միջնադարյան հայկական արծաթե զարդերի հավաքածու',
            year=1200,
            image_url='https://example.com/jewelry.jpg',
            user_id=1
        ),
        Artifact(
            name='Հին ձեռագիր',
            description='12-րդ դարի հայկական ձեռագիր մատյան',
            year=1150,
            image_url='https://example.com/manuscript.jpg',
            user_id=1
        )
    ]
    
    for artifact in artifacts:
        db.session.add(artifact)
    db.session.commit()
    
    # Ստեղծում ենք ցուցադրություններ
    today = datetime.now().date()
    
    exhibitions = [
        Exhibition(
            title='Հին Հայաստանի գանձերը',
            description='Ցուցադրությունը ներկայացնում է հին հայկական մշակույթի բացառիկ նմուշներ',
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=20),
            image_url='https://example.com/exhibition1.jpg',
            user_id=1
        ),
        Exhibition(
            title='Միջնադարյան արվեստ',
            description='Հայկական միջնադարյան արվեստի հատընտիր նմուշների ցուցադրություն',
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=60),
            image_url='https://example.com/exhibition2.jpg',
            user_id=1
        )
    ]
    
    # Ավելացնում ենք նմուշները ցուցադրություններին
    exhibitions[0].artifacts.extend(artifacts[:2])  # Առաջին երկու նմուշները
    exhibitions[1].artifacts.append(artifacts[2])   # Երրորդ նմուշը
    
    for exhibition in exhibitions:
        db.session.add(exhibition)
    db.session.commit()
    
print("Տվյալների բազան հաջողությամբ ստեղծվեց")
    
print("Տվյալների բազան հաջողությամբ ստեղծվեց")