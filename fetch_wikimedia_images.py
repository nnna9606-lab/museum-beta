#!/usr/bin/env python3
"""Fetch images from Wikimedia Commons and update artifact/exhibition image URLs.
This script searches Commons for file pages matching the artifact/exhibition name
and updates the database to point to the file's URL. It also adds multiple
images for exhibitions as `ExhibitionImage` rows.
"""
import requests
from app import app, db, Artifact, Exhibition, ExhibitionImage
import sys


def sp(msg):
    try:
        # write UTF-8 safely to the console
        sys.stdout.buffer.write((str(msg) + "\n").encode('utf-8'))
    except Exception:
        # fallback
        print(msg)

API_ENDPOINT = 'https://commons.wikimedia.org/w/api.php'


def get_commons_image_url(query):
    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': query,
        'gsrnamespace': 6,  # Namespace 6 = File
        'gsrlimit': 1,
        'prop': 'imageinfo',
        'iiprop': 'url'
    }
    try:
        headers = {
            'User-Agent': 'MuseumSite/1.0 (contact: admin@example.com)'
        }
        r = requests.get(API_ENDPOINT, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        for pid, p in pages.items():
            iinfo = p.get('imageinfo')
            if iinfo and isinstance(iinfo, list):
                return iinfo[0].get('url')
    except Exception as e:
        sp(f'  ✗ Error searching Commons for "{query}": {e}')
    return None


with app.app_context():
    sp('Fetching Commons images for artifacts...')
    artifacts = Artifact.query.all()
    for art in artifacts:
        # Use shorter search term
        term = art.name
        sp(f' - Searching for artifact: {term}')
        url = get_commons_image_url(term)
        if url:
            art.image_url = url
            # remove any additional ArtifactImage rows since main image is external
            ArtifactImage = globals().get('ArtifactImage')
            if ArtifactImage:
                ArtifactImage.query.filter_by(artifact_id=art.id).delete()
            sp(f'   ✓ Found: {url}')
        else:
            sp(f'   - No image found for: {term}')

    sp('\nFetching Commons images for exhibitions (multiple per exhibition)...')
    exhibitions = Exhibition.query.all()
    for ex in exhibitions:
        term = ex.title
        sp(f' - Searching for exhibition: {term}')
        # try 3 variations: title, title + museum, title + artifact
        candidates = [term, f"{term} museum", f"{term} artifacts"]
        added = 0
        for c in candidates:
            if added >= 3:
                break
            url = get_commons_image_url(c)
            if url:
                img = ExhibitionImage(exhibition_id=ex.id, image_url=url)
                db.session.add(img)
                added += 1
                sp(f'   ✓ Added: {url}')
        if added == 0:
            sp(f'   - No images found for exhibition: {term}')

    db.session.commit()
    sp('\nDone updating Commons images.')
