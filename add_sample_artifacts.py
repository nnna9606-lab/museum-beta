from app import app, db, Artifact, User, ArtifactImage
from datetime import datetime
import json

def create_sample_artifacts():
    # Ստեղծել admin օգտատեր, եթե չկա
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@museum.am',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    # Նմուշների տվյալներ մի քանի նկարներով
    artifacts_data = [
        {
            "name": "Ուրարտական Վահան",
            "description": "Բրոնզե վահան՝ զարդարված առյուծի և ցուլի պատկերներով: Հայտնաբերվել է Կարմիր բլուր հնավայրում: Վահանի վրա պատկերված են նաև երկրաչափական զարդանախշեր և սեպագիր արձանագրություն:",
            "year": -785,  # Ք.ա. 785
            "category": "archaeological",
            "tags": json.dumps(["ուրարտու", "զենք", "բրոնզ", "պաշտպանություն"]),
            "image_url": "urartian_shield.jpg",
            "images": ["urartian_shield_1.jpg", "urartian_shield_2.jpg", "urartian_shield_3.jpg"]
        },
        {
            "name": "Արծաթե Գավաթ Անիից",
            "description": "Միջնադարյան արծաթե գավաթ՝ ձեռագործ քանդակազարդումներով: Պատրաստվել է Անիի արհեստանոցներում: Գավաթի վրա պատկերված են որսի տեսարաններ և բուսական զարդանախշեր:",
            "year": 1215,
            "category": "historical",
            "tags": json.dumps(["անի", "արծաթագործություն", "միջնադար", "սպասք"]),
            "image_url": "ani_silver_cup.jpg",
            "images": ["ani_silver_cup_1.jpg", "ani_silver_cup_2.jpg", "ani_silver_cup_3.jpg"]
        },
        {
            "name": "Հայ Դասական Ներկ",
            "description": "Յուղաներկ կտավ՝ պատկերող բնական տեսարան: Հայ դասական նկարիչի ստեղծագործություն: Նկարը արտացոլում է հայ մշակույթի և բնության գեղեցկությունը:",
            "year": 1885,
            "category": "art",
            "tags": json.dumps(["հայ", "նկարիչ", "բնական", "տեսարան"]),
            "image_url": "classical_painting.jpg",
            "images": ["classical_painting_1.jpg", "classical_painting_2.jpg", "classical_painting_3.jpg"]
        },
        {
            "name": "Երևանի Կապույտ Մզկիթի Կաշին",
            "description": "Պատի կապույտ կաշի՝ բուսական զարդանախշերով: Պահպանվել է Երևանի Կապույտ մզկիթի վերականգնման ժամանակ: Արտացոլում է 18-րդ դարի պարսկական ճարտարապետական ոճը:",
            "year": 1765,
            "category": "cultural",
            "tags": json.dumps(["ճարտարապետություն", "կաշի", "մզկիթ", "երևան"]),
            "image_url": "blue_mosque_tile.jpg",
            "images": ["blue_mosque_tile_1.jpg", "blue_mosque_tile_2.jpg", "blue_mosque_tile_3.jpg"]
        },
        {
            "name": "Հնագույն Պղնձե Զանգ",
            "description": "Պղնձից կռած զանգ՝ հայտնաբերված Լոռու մարզի հնավայրերից մեկում: Զանգի վրա առկա են քրիստոնեական խորհրդանիշներ և հայերեն արձանագրություն:",
            "year": 1134,
            "category": "archaeological",
            "tags": json.dumps(["զանգ", "պղինձ", "քրիստոնեություն", "լոռի"]),
            "image_url": "ancient_bell.jpg",
            "images": ["ancient_bell_1.jpg", "ancient_bell_2.jpg", "ancient_bell_3.jpg"]
        }
    ]

    # Ավելացնել նմուշները
    for data in artifacts_data:
        # Ստուգել՝ արդյոք նմուշը արդեն գոյություն ունի
        existing = Artifact.query.filter_by(name=data['name']).first()
        if not existing:
            artifact = Artifact(
                name=data['name'],
                description=data['description'],
                year=data['year'],
                category=data['category'],
                tags=data['tags'],
                image_url=data['image_url'],
                user_id=admin.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(artifact)
            db.session.flush()  # բերել չկամայական ID
            
            # Ավելացնել նկարները
            for img_url in data.get('images', []):
                artifact_image = ArtifactImage(
                    artifact_id=artifact.id,
                    image_url=img_url
                )
                db.session.add(artifact_image)
            
            print(f"Ավելացվեց՝ {data['name']}")
        else:
            print(f"Արդեն գոյություն ունի՝ {data['name']}")

    # Պահպանել փոփոխությունները
    db.session.commit()
    print("Նմուշների ավելացումը ավարտվեց")

if __name__ == '__main__':
    with app.app_context():
        create_sample_artifacts()