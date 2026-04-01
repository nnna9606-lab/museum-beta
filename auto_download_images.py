#!/usr/bin/env python3
"""Auto-download images from free sources (Unsplash, Pexels, Pixabay)
for artifacts and exhibitions, and populate the database.
"""
import os
import sys
import hashlib
import requests
from urllib.parse import urlparse
import time

from app import app, db, Artifact, ArtifactImage, Exhibition, ExhibitionImage


def sp(msg):
    """Safe print to handle UTF-8 with Windows console"""
    try:
        sys.stdout.buffer.write((str(msg) + "\n").encode('utf-8'))
    except Exception:
        print(msg)


def safe_ext_from_url(url, default='.jpg'):
    """Extract file extension from URL"""
    p = urlparse(url)
    base = os.path.basename(p.path)
    if '.' in base:
        ext = os.path.splitext(base)[1]
        if len(ext) <= 5:
            return ext
    return default


def download(url, dest_path, retries=3):
    """Download a file with retries"""
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    headers = {'User-Agent': ua}
    
    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, headers=headers, stream=True, timeout=15, allow_redirects=True) as r:
                r.raise_for_status()
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return True
        except Exception as e:
            if attempt < retries:
                sp(f'    retry {attempt}/{retries}...')
                time.sleep(attempt)
            else:
                sp(f'    ✗ Failed: {e}')
    return False


def make_filename(prefix, obj_id, url, ext):
    """Generate a unique safe filename"""
    h = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
    name = f"{prefix}_{obj_id}_{h}{ext}"
    return name


def get_image_url(obj_type='artifact', attempt=1):
    """Get a random image URL from Unsplash public endpoint
    (no API key required).
    
    Returns: https://source.unsplash.com/800x600/?keyword
    """
    # Keywords for different object types and attempts
    artifact_kws = [
        'museum,ancient',
        'artifact,history',
        'antique,artifact',
        'historical,artifact',
        'ancient,artifact',
    ]
    exhibition_kws = [
        'gallery,museum',
        'art,exhibition',
        'museum,collection',
        'gallery,art',
        'exhibition,history',
    ]
    
    if obj_type == 'exhibition':
        kws = exhibition_kws
    else:
        kws = artifact_kws
    
    # Use different keywords for different attempts
    kw_idx = (attempt - 1) % len(kws)
    kw = kws[kw_idx]
    
    url = f'https://source.unsplash.com/800x600/?{kw}'
    return url


with app.app_context():
    upload_dir = os.path.join(os.path.dirname(__file__), app.config.get('UPLOAD_FOLDER', 'static/uploads'))
    os.makedirs(upload_dir, exist_ok=True)

    sp('')
    sp('=== AUTO-DOWNLOADING ARTIFACT IMAGES ===')
    
    with db.session.no_autoflush:
        artifacts = Artifact.query.all()
    
    art_count = 0
    for i, art in enumerate(artifacts):
        sp(f'[{art.id}] {art.get_name("hy")}')
        
        # Get a random image URL (no search term needed)
        url = get_image_url('artifact', attempt=i+1)
        sp(f'  Trying: {url}')
        
        ext = '.jpg'
        filename = make_filename('artifact', art.id, url, ext)
        dest = os.path.join(upload_dir, filename)
        
        if download(url, dest):
            art.image_url = filename
            art_count += 1
            sp(f'  ✓ Saved: {filename}')
        else:
            sp(f'  Could not download')
        
        time.sleep(0.3)  # Rate limit
    
    try:
        db.session.commit()
        sp(f'\n✓ Committed {art_count} artifact images')
    except Exception as e:
        db.session.rollback()
        sp(f'✗ Error committing artifacts: {e}')

    sp('')
    sp('=== AUTO-DOWNLOADING EXHIBITION IMAGES ===')
    
    with db.session.no_autoflush:
        exhibitions = Exhibition.query.all()
    
    ex_count = 0
    total_images = 0
    for ex_idx, ex in enumerate(exhibitions):
        sp(f'[{ex.id}] {ex.get_title("hy")}')
        
        # Try to add 2 images per exhibition
        for i in range(2):
            url = get_image_url('exhibition', attempt=ex_idx * 3 + i + 1)
            sp(f'  Attempting image {i+1}...')
            
            ext = '.jpg'
            filename = make_filename('eximg', ex.id, url, ext)
            dest = os.path.join(upload_dir, filename)
            
            if download(url, dest):
                img = ExhibitionImage(exhibition_id=ex.id, image_url=filename)
                db.session.add(img)
                total_images += 1
                sp(f'  ✓ Added image: {filename}')
                ex_count += 1
            else:
                sp(f'  Image {i+1} download failed')
            
            time.sleep(0.3)
        
        # Commit after each exhibition to avoid large pending flushes
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            sp(f'  ✗ Error committing exhibition {ex.id}: {e}')
    
    sp(f'\n✓ Downloaded {total_images} exhibition images')
    sp('\nDownload complete!')
