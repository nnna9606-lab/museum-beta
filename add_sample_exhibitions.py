from datetime import datetime, date, timedelta
from app import app, db, Exhibition, Artifact, User


def create_sample_exhibitions():
    with app.app_context():
        # Ensure there's at least one admin or user to attribute the exhibitions to
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='script_user', email='script@museum.local', role='admin')
            admin.set_password('password')
            db.session.add(admin)
            db.session.commit()

        # Prepare sample exhibitions
        today = date.today()
        exhibitions = [
            {
                'title': 'Ուրարտական ժառանգություն',
                'description': 'Ցուցադրություն՝ ուրարտական ժամանակաշրջանի զարդարանքներ և զինատեսակներ՝ բրոնզից և գրիդից։',
                'start_date': today - timedelta(days=365*3),
                'end_date': today - timedelta(days=365*2),
                'image_url': 'urartian_shield.jpg',
                'location': 'Աստորացված սրահ 1',
                'artifact_names': [
                    'Ուրարտական Վահան',
                ]
            },
            {
                'title': 'Անիի արհեստանոցներ',
                'description': 'Միջնադարյան արծաթագործության նմուշներ և առօրյա առարկաներ՝ Անի քաղաքից։',
                'start_date': today - timedelta(days=400),
                'end_date': today + timedelta(days=200),  # currently active
                'image_url': 'ani_silver_cup.jpg',
                'location': 'Պահեստ-ցուցասրահ 3',
                'artifact_names': [
                    'Արծաթե Գավաթ Անիից',
                ]
            },
            {
                'title': 'Հայ Դասական Արվեստ',
                'description': 'Դասական երկրոմ շրջանի հայ արվեստի ցուցադրություն՝ տեսարանապատկերներ և մշակութային արտաստեղծումներ։',
                'start_date': today - timedelta(days=20),
                'end_date': today + timedelta(days=90),  # active
                'image_url': 'classical_painting.jpg',
                'location': 'Գլխավոր սրահ',
                'artifact_names': [
                    'Հայ Դասական Ներկ',
                ]
            },
            {
                'title': 'Ծեսեր և ձեռագործություն',
                'description': 'Թանգարանային հավաքածու՝ կրոնական առարկաներ և ծեսական սպասք՝ տարբեր շրջաններից։',
                'start_date': today + timedelta(days=30),  # upcoming
                'end_date': today + timedelta(days=365),
                'image_url': 'blue_mosque_tile.jpg',
                'location': 'Մշակութային սրահ',
                'artifact_names': [
                    'Երևանի Կապույտ Մզկիթի Կաշին',
                ]
            },
            {
                'title': 'Հնագույն ձայներ',
                'description': 'Խորհրդանշական ցուցադրություն՝ հնագույն երաժշտական և աղոթքային գործիքներ, զանգեր և արարողակարգեր։',
                'start_date': today - timedelta(days=800),
                'end_date': today - timedelta(days=500),
                'image_url': 'ancient_bell.jpg',
                'location': 'Հնագիտության անկյուն',
                'artifact_names': [
                    'Հնագույն Պղնձե Զանգ',
                    'Հաղպատի Վանքի Զանգ'
                ]
            }
        ]

        created = []
        for ex in exhibitions:
            # skip if an exhibition with same title exists
            if Exhibition.query.filter_by(title=ex['title']).first():
                print(f"Կտրված ցուցադրություն արդեն գոյություն ունի՝ {ex['title']}")
                continue

            new_ex = Exhibition(
                title=ex['title'],
                description=ex['description'],
                start_date=ex['start_date'],
                end_date=ex['end_date'],
                image_url=ex['image_url'],
                user_id=admin.id,
            )

            # attach artifacts by name when possible
            for name in ex.get('artifact_names', []):
                art = Artifact.query.filter(Artifact.name.ilike(f"%{name}%")).first()
                if art:
                    new_ex.artifacts.append(art)

            db.session.add(new_ex)
            created.append(ex['title'])

        db.session.commit()

        print(f"Ստեղծվեց ցուցադրություններ՝ {created}")


if __name__ == '__main__':
    create_sample_exhibitions()
