# Set external image URLs (Unsplash-based) for artifacts and exhibitions
from app import app, db, Artifact, Exhibition, ArtifactImage

mapping_artifacts = {
    'Ուրարտական Վահան': 'https://source.unsplash.com/600x400/?shield,ancient',
    'Արծաղե Զարդեր': 'https://source.unsplash.com/600x400/?jewelry,ancient',
    'Հային Դասական Ներկ': 'https://source.unsplash.com/600x400/?painting,classic',
    'Երևանի Կապույտ Մզկիթի Կաշին': 'https://source.unsplash.com/600x400/?tile,pattern',
    'Հնագույն Պղնձե Զանգ': 'https://source.unsplash.com/600x400/?bell,ancient',
    'Ձեռագիր մատյան': 'https://source.unsplash.com/600x400/?manuscript,book'
}

mapping_exhibitions = {
    'Ուրարտական Ժառանգություն': 'https://source.unsplash.com/600x400/?urartu,museum',
    'Հայկական Զարդեր և Դրամ': 'https://source.unsplash.com/600x400/?coins,jewelry',
    'Հայ Դասական Արվեստ': 'https://source.unsplash.com/600x400/?classical,art',
    'Ծեսեր և Ձեռագործություն': 'https://source.unsplash.com/600x400/?ceremony,craft',
    'Հնագույն Ձայներ': 'https://source.unsplash.com/600x400/?ancient,music'
}

with app.app_context():
    print('Updating artifact image URLs...')
    for name, url in mapping_artifacts.items():
        art = Artifact.query.filter(Artifact.name.ilike(f"%{name}%")).first()
        if art:
            art.image_url = url
            # remove additional ArtifactImage rows (we'll store external images as main image)
            ArtifactImage.query.filter_by(artifact_id=art.id).delete()
            print(f'  - Updated {art.name} -> {url}')

    print('Updating exhibition image URLs...')
    for title, url in mapping_exhibitions.items():
        ex = Exhibition.query.filter(Exhibition.title.ilike(f"%{title}%")).first()
        if ex:
            ex.image_url = url
            print(f'  - Updated {ex.title} -> {url}')

    db.session.commit()
    print('Done.')
