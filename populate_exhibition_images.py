#!/usr/bin/env python3
"""Populate ExhibitionImage rows with external image URLs (Unsplash source).
This creates multiple images per exhibition so you can manage (view/delete) them from the UI.
"""
from app import app, db, Exhibition, ExhibitionImage

mapping = {
    'Ուրարտական Ժառանգություն': [
        'https://source.unsplash.com/800x600/?urartu,archaeology',
        'https://source.unsplash.com/800x600/?ancient,bronze',
        'https://source.unsplash.com/800x600/?shield,artifact'
    ],
    'Հայկական Զարդեր և Դրամ': [
        'https://source.unsplash.com/800x600/?coins,jewelry',
        'https://source.unsplash.com/800x600/?silver,ornament',
        'https://source.unsplash.com/800x600/?medieval,jewelry'
    ],
    'Հայ Դասական Արվեստ': [
        'https://source.unsplash.com/800x600/?classical,painting',
        'https://source.unsplash.com/800x600/?landscape,painting',
        'https://source.unsplash.com/800x600/?oil,canvas'
    ],
    'Ծեսեր և Ձեռագործություն': [
        'https://source.unsplash.com/800x600/?ceremony,ritual',
        'https://source.unsplash.com/800x600/?craft,handmade',
        'https://source.unsplash.com/800x600/?textile,pattern'
    ],
    'Հնագույն Ձայներ': [
        'https://source.unsplash.com/800x600/?ancient,music',
        'https://source.unsplash.com/800x600/?musical,instrument',
        'https://source.unsplash.com/800x600/?bell,ancient'
    ]
}

with app.app_context():
    for title, urls in mapping.items():
        ex = Exhibition.query.filter(Exhibition.title.ilike(f"%{title}%")).first()
        if not ex:
            print(f"Exhibition not found: {title}")
            continue
        # add images if none exist
        if ex.images:
            print(f"Exhibition '{ex.title}' already has images ({len(ex.images)})")
            continue
        for u in urls:
            img = ExhibitionImage(exhibition_id=ex.id, image_url=u)
            db.session.add(img)
        print(f"Added {len(urls)} images to '{ex.title}'")
    db.session.commit()
    print('Done.')
