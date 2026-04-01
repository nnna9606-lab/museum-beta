#!/usr/bin/env python3
"""Download external image URLs (Wikimedia/Unsplash) into static/uploads
and update Artifact.image_url, ArtifactImage.image_url, ExhibitionImage.image_url
to point to the local filenames.
"""
import os
import re
import hashlib
import requests
import sys
from urllib.parse import urlparse

from app import app, db, Artifact, ArtifactImage, ExhibitionImage


def sp(msg):
    try:
        sys.stdout.buffer.write((str(msg) + "\n").encode('utf-8'))
    except Exception:
        print(msg)


def safe_ext_from_url(url, default='.jpg'):
    p = urlparse(url)
    base = os.path.basename(p.path)
    if '.' in base:
        ext = os.path.splitext(base)[1]
        if len(ext) <= 5:
            return ext
    # fallback by content-type HEAD
    try:
        headers = {'User-Agent': 'MuseumSite/1.0 (contact: admin@example.com)'}
        r = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        ctype = r.headers.get('content-type', '')
        if 'jpeg' in ctype:
            return '.jpg'
        if 'png' in ctype:
            return '.png'
        if 'gif' in ctype:
            return '.gif'
    except Exception:
        pass
    return default


def download(url, dest_path):
    # Use a browser-like User-Agent to improve success with remote hosts
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    headers = {'User-Agent': ua}
    # Retry logic
    for attempt in range(1, 4):
        try:
            with requests.get(url, headers=headers, stream=True, timeout=30, allow_redirects=True) as r:
                # Some hosts block HEAD requests; check status and content-type
                r.raise_for_status()
                # If the response is not binary image-like (e.g. HTML error page), still try to save
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return True
        except requests.exceptions.HTTPError as he:
            # Try again with a Referer for Wikimedia-hosted files
            if r is not None and r.status_code == 403 and 'upload.wikimedia.org' in url:
                try:
                    headers['Referer'] = 'https://commons.wikimedia.org'
                    with requests.get(url, headers=headers, stream=True, timeout=30, allow_redirects=True) as r2:
                        r2.raise_for_status()
                        with open(dest_path, 'wb') as f:
                            for chunk in r2.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                    return True
                except Exception:
                    pass
            sp(f'  attempt {attempt} HTTP error for {url}: {he}')
        except Exception as e:
            sp(f'  attempt {attempt} error downloading {url}: {e}')
        # small backoff
        import time
        time.sleep(attempt)
    sp(f'  ✗ Failed to download {url} after retries')
    return False


def make_filename(prefix, obj_id, url, ext):
    h = hashlib.md5(url.encode('utf-8')).hexdigest()[:10]
    name = f"{prefix}_{obj_id}_{h}{ext}"
    # sanitize
    name = re.sub(r'[^A-Za-z0-9_.-]', '_', name)
    return name


with app.app_context():
    upload_dir = os.path.join(os.path.dirname(__file__), app.config.get('UPLOAD_FOLDER', 'static/uploads'))
    os.makedirs(upload_dir, exist_ok=True)

    sp('Scanning artifacts for external images...')
    with db.session.no_autoflush:
        artifacts = Artifact.query.filter(Artifact.image_url != None).all()
    art_downloaded = 0
    for art in artifacts:
        url = art.image_url
        if not url or not url.startswith('http'):
            continue
        ext = safe_ext_from_url(url)
        filename = make_filename('artifact', art.id, url, ext)
        dest = os.path.join(upload_dir, filename)
        if download(url, dest):
            art.image_url = filename
            art_downloaded += 1
            sp(f'  ✓ Saved artifact {art.id} -> {filename}')

    sp(f'Downloaded {art_downloaded} artifact main images')
    # commit after artifact batch to avoid large pending flush
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    sp('Scanning ArtifactImage rows...')
    with db.session.no_autoflush:
        aimgs = ArtifactImage.query.filter(ArtifactImage.image_url != None).all()
    ai_downloaded = 0
    for ai in aimgs:
        url = ai.image_url
        if not url or not url.startswith('http'):
            continue
        ext = safe_ext_from_url(url)
        filename = make_filename('artimg', ai.id, url, ext)
        dest = os.path.join(upload_dir, filename)
        if download(url, dest):
            ai.image_url = filename
            ai_downloaded += 1
            sp(f'  ✓ Saved artifact image {ai.id} -> {filename}')

    sp(f'Downloaded {ai_downloaded} ArtifactImage rows')
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    sp('Scanning ExhibitionImage rows...')
    with db.session.no_autoflush:
        eimgs = ExhibitionImage.query.filter(ExhibitionImage.image_url != None).all()
    ei_downloaded = 0
    for ei in eimgs:
        url = ei.image_url
        if not url or not url.startswith('http'):
            continue
        ext = safe_ext_from_url(url)
        filename = make_filename('eximg', ei.id, url, ext)
        dest = os.path.join(upload_dir, filename)
        if download(url, dest):
            ei.image_url = filename
            ei_downloaded += 1
            sp(f'  ✓ Saved exhibition image {ei.id} -> {filename}')

    sp(f'Downloaded {ei_downloaded} ExhibitionImage rows')

    try:
        db.session.commit()
        sp('DB updated with local filenames.')
    except Exception as e:
        db.session.rollback()
        sp(f'Failed to commit DB changes: {e}')

    sp('Mirror complete.')
