#!/usr/bin/env python3
"""
Complete setup script - initializes database with all artifacts and exhibitions
"""
from app import app, db, Artifact, Exhibition, ArtifactImage, User
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont
import os
import json

def create_sample_image(filename, width=400, height=300, text=""):
    """Create a sample image for testing"""
    os.makedirs('static/uploads', exist_ok=True)
    filepath = os.path.join('static/uploads', filename)
    
    # Generate color based on text
    colors = {
        'shield': (178, 140, 100),  # brown
        'cup': (192, 192, 192),     # silver
        'painting': (200, 100, 50), # orange-brown
        'tile': (65, 105, 225),     # royal blue
        'bell': (184, 134, 11),     # goldenrod
    }
    
    color = (100, 100, 100)  # default gray
    for key, c in colors.items():
        if key in filename:
            color = c
            break
    
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)
    
    # Add text
    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    if text:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    img.save(filepath)
    print(f"  ✓ Image created: {filename}")
    return filename

def setup_database():
    with app.app_context():
        # Create all tables
        print("🔍 Creating database tables...")
        db.create_all()
        print("✓ Database tables created")
        
        # Create admin user
        print("\n👤 Setting up admin user...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@museum.am',
                role='admin',
                created_at=datetime.utcnow()
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created (username: admin, password: admin123)")
        else:
            print("✓ Admin user already exists")
        
        # Create sample images
        print("\n🖼️  Creating sample images...")
        image_files = {
            'urartian_shield.jpg': 'Ուրարտական Վահան',
            'urartian_shield_1.jpg': 'Shield 1',
            'urartian_shield_2.jpg': 'Shield 2',
            'urartian_shield_3.jpg': 'Shield 3',
            'ani_silver_cup.jpg': 'Արծաթե Գավաթ',
            'ani_silver_cup_1.jpg': 'Cup 1',
            'ani_silver_cup_2.jpg': 'Cup 2',
            'ani_silver_cup_3.jpg': 'Cup 3',
            'classical_painting.jpg': 'Դասական Ներկ',
            'classical_painting_1.jpg': 'Paint 1',
            'classical_painting_2.jpg': 'Paint 2',
            'classical_painting_3.jpg': 'Paint 3',
            'blue_mosque_tile.jpg': 'Կապույտ Մզկիթ',
            'blue_mosque_tile_1.jpg': 'Tile 1',
            'blue_mosque_tile_2.jpg': 'Tile 2',
            'blue_mosque_tile_3.jpg': 'Tile 3',
            'ancient_bell.jpg': 'Հնագույն Զանգ',
            'ancient_bell_1.jpg': 'Bell 1',
            'ancient_bell_2.jpg': 'Bell 2',
            'ancient_bell_3.jpg': 'Bell 3',
        }
        
        for fname, desc in image_files.items():
            if not os.path.exists(os.path.join('static/uploads', fname)):
                create_sample_image(fname, text=desc)
        
        # Create artifacts
        print("\n🏺 Creating artifacts...")
        artifacts_data = [
            {
                "name": "Ուրարտական Վահան",
                "description": "Բրոնզե վահան՝ զարդարված առյուծի և ցուլի պատկերներով: Հայտնաբերվել է Կարմիր բլուր հնավայրում: Վահանի վրա պատկերված են նաև երկրաչափական զարդանախշեր և սեպագիր արձանագրություն:",
                "year": -785,
                "category": "archaeological",
                "tags": json.dumps(["ուրարտու", "զենք", "բրոնզ", "պաշտպանություն"]),
                "image_url": "urartian_shield.jpg",
                "images": ["urartian_shield_1.jpg", "urartian_shield_2.jpg", "urartian_shield_3.jpg"]
            },
            {
                "name": "Արծաղե Զարդեր",
                "description": "Արծաղե զարդեր՝ ջահել հայերի ժամանակից: Բաղկացած կանացի լուսային և առանցքային տաղավարից: Սուրբ հայտնի գանձ, որ պահվել է շատ տարիներ:",
                "year": -200,
                "category": "archaeological",
                "tags": json.dumps(["արծաղե", "զարդ", "հույն", "տաղավար"]),
                "image_url": "ani_silver_cup.jpg",
                "images": ["ani_silver_cup_1.jpg", "ani_silver_cup_2.jpg", "ani_silver_cup_3.jpg"]
            },
            {
                "name": "Հային Դասական Ներկ",
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
        
        artifacts_map = {}
        for data in artifacts_data:
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
                db.session.flush()
                
                # Add artifact images
                for img_url in data.get('images', []):
                    artifact_image = ArtifactImage(
                        artifact_id=artifact.id,
                        image_url=img_url
                    )
                    db.session.add(artifact_image)
                
                artifacts_map[data['name']] = artifact
                print(f"  ✓ {data['name']}")
            else:
                artifacts_map[data['name']] = existing
                print(f"  ⊘ {data['name']} (already exists)")
        
        db.session.commit()
        
        # Create exhibitions
        print("\n🎭 Creating exhibitions...")
        today = date.today()
        exhibitions_data = [
            {
                'title': 'Ուրարտական Ժառանգություն',
                'description': 'Ցուցադրություն՝ ուրարտական ժամանակաշրջանի զարդարանքներ և զինատեսակներ՝ բրոնզից և գրիդից։',
                'start_date': today - timedelta(days=365*3),
                'end_date': today - timedelta(days=365*2),
                'image_url': 'urartian_shield.jpg',
                'artifact_names': ['Ուրարտական Վահան']
            },
            {
                'title': 'Հայկական Զարդեր և Դրամ',
                'description': 'Միջնադարյան արծաղե և աշխատանք՝ հայերի փողից: Շատ կարևոր հավաքածու ցուցադրվում է:',
                'start_date': today - timedelta(days=400),
                'end_date': today + timedelta(days=200),
                'image_url': 'ani_silver_cup.jpg',
                'artifact_names': ['Արծաղե Զարդեր']
            },
            {
                'title': 'Հայ Դասական Արվեստ',
                'description': 'Դասական երկրոմ շրջանի հայ արվեստի ցուցադրություն՝ տեսարանապատկերներ և մշակութային արտաստեղծումներ։',
                'start_date': today - timedelta(days=20),
                'end_date': today + timedelta(days=90),
                'image_url': 'classical_painting.jpg',
                'artifact_names': ['Հային Դասական Ներկ']
            },
            {
                'title': 'Ծեսեր և Ձեռագործություն',
                'description': 'Թանգարանային հավաքածու՝ կրոնական առարկաներ և ծեսական սպասք՝ տարբեր շրջաններից։',
                'start_date': today + timedelta(days=30),
                'end_date': today + timedelta(days=365),
                'image_url': 'blue_mosque_tile.jpg',
                'artifact_names': ['Երևանի Կապույտ Մզկիթի Կաշին']
            },
            {
                'title': 'Հնագույն Ձայներ',
                'description': 'Խորհրդանշական ցուցադրություն՝ հնագույն երաժշտական և աղոթքային գործիքներ, զանգեր և արարողակարգեր։',
                'start_date': today - timedelta(days=800),
                'end_date': today - timedelta(days=500),
                'image_url': 'ancient_bell.jpg',
                'artifact_names': ['Հնագույն Պղնձե Զանգ']
            }
        ]
        
        for ex_data in exhibitions_data:
            existing = Exhibition.query.filter_by(title=ex_data['title']).first()
            if not existing:
                new_ex = Exhibition(
                    title=ex_data['title'],
                    description=ex_data['description'],
                    start_date=ex_data['start_date'],
                    end_date=ex_data['end_date'],
                    image_url=ex_data['image_url'],
                    user_id=admin.id
                )
                
                # Attach artifacts by name
                for artifact_name in ex_data.get('artifact_names', []):
                    if artifact_name in artifacts_map:
                        new_ex.artifacts.append(artifacts_map[artifact_name])
                
                db.session.add(new_ex)
                print(f"  ✓ {ex_data['title']}")
            else:
                print(f"  ⊘ {ex_data['title']} (already exists)")
        
        db.session.commit()
        
        # Verify counts
        print("\n📊 Verification:")
        artifact_count = Artifact.query.count()
        exhibition_count = Exhibition.query.count()
        image_count = ArtifactImage.query.count()
        
        print(f"  ✓ Artifacts: {artifact_count}")
        print(f"  ✓ Exhibitions: {exhibition_count}")
        print(f"  ✓ Artifact Images: {image_count}")
        print(f"  ✓ Images on disk: {len(os.listdir('static/uploads'))}")
        
        print("\n✅ Setup Complete!")

if __name__ == '__main__':
    setup_database()
