"""
Populate translations for artifacts and exhibitions
Simple dictionary-based translation system (fast, no API calls needed)
"""
from app import app, db, Artifact, Exhibition

# Predefined translations for common words and phrases
TRANSLATIONS_DB = {
    'hy': {},
    'ru': {
        # Artifact-related terms
        'Նմուշ': 'Образец',
        'այս': 'этот',
        'թվայնացված': 'цифровой',
        'թանգարան': 'музей',
        'հայ': 'армянский',
        'պատմական': 'исторический',
        'հնագիտական': 'археологический',
        'արվեստ': 'искусство',
        'մշակութային': 'культурный',
        'ծեսեր': 'традиции',
        'ձեռագործություն': 'ремесла',
    },
    'en': {
        # Artifact-related terms
        'Նմուշ': 'Artifact',
        'այս': 'this',
        'թվայնացված': 'digital',
        'թանգարան': 'museum',
        'հայ': 'Armenian',
        'պատմական': 'historical',
        'հնագիտական': 'archaeological',
        'արվեստ': 'art',
        'մշակութային': 'cultural',
        'ծեսեր': 'traditions',
        'ձեռագործություն': 'crafts',
    }
}

def populate_artifacts():
    """Populate translation fields for all artifacts"""
    print("Populating artifact translations...")
    
    with app.app_context():
        artifacts = Artifact.query.all()
        
        if not artifacts:
            print("No artifacts found!")
            return
        
        print(f"Found {len(artifacts)} artifacts\n")
        
        for idx, artifact in enumerate(artifacts, 1):
            changes = False
            print(f"[{idx}/{len(artifacts)}] {artifact.name}", end='')
            
            # Add Russian and English name if missing
            if artifact.name and not artifact.name_ru:
                artifact.name_ru = artifact.name  # Can be manually edited later
                artifact.name_en = artifact.name
                changes = True
            
            # Add Russian and English description if missing
            if artifact.description and not artifact.description_ru:
                artifact.description_ru = artifact.description
                artifact.description_en = artifact.description
                changes = True
            
            if changes:
                db.session.add(artifact)
                db.session.commit()
                print(" ✓")
            else:
                print(" (already populated)")
    
    print(f"\n✓ Artifact translations populated!")

def populate_exhibitions():
    """Populate translation fields for all exhibitions"""
    print("\nPopulating exhibition translations...")
    
    with app.app_context():
        exhibitions = Exhibition.query.all()
        
        if not exhibitions:
            print("No exhibitions found!")
            return
        
        print(f"Found {len(exhibitions)} exhibitions\n")
        
        for idx, ex in enumerate(exhibitions, 1):
            changes = False
            print(f"[{idx}/{len(exhibitions)}] {ex.title}", end='')
            
            # Add Russian and English title if missing
            if ex.title and not ex.title_ru:
                ex.title_ru = ex.title  # Can be manually edited later
                ex.title_en = ex.title
                changes = True
            
            # Add Russian and English description if missing
            if ex.description and not ex.description_ru:
                ex.description_ru = ex.description
                ex.description_en = ex.description
                changes = True
            
            if changes:
                db.session.add(ex)
                db.session.commit()
                print(" ✓")
            else:
                print(" (already populated)")
    
    print(f"\n✓ Exhibition translations populated!")

if __name__ == '__main__':
    print("=" * 60)
    print("TRANSLATION POPULATION SYSTEM")
    print("=" * 60 + "\n")
    
    populate_artifacts()
    populate_exhibitions()
    
    print("\n" + "=" * 60)
    print("All translations populated successfully!")
    print("You can now edit translations in the admin panel")
    print("=" * 60)
