#!/usr/bin/env python3
"""Բոլոր նմուշների նկարը կապում է static/uploads-ի jpg ֆայլերին ըստ անունների"""
import os
from app import app, db, Artifact

with app.app_context():
    upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    files = os.listdir(upload_dir)
    jpg_files = [f for f in files if f.lower().endswith('.jpg')]
    count = 0
    for art in Artifact.query.all():
        # Փնտրում ենք ֆայլ, որի անունը պարունակում է նմուշի անունը (հայերեն)
        for fname in jpg_files:
            if art.name.replace(' ','') in fname.replace(' ',''):
                art.image_url = fname
                count += 1
                break
    db.session.commit()
    print(f"{count} նմուշի նկար կապվեց jpg ֆայլին static/uploads-ում")
