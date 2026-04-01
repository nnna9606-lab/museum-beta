#!/usr/bin/env python3
"""Բոլոր ցուցադրությունների նկարը կապում է static/uploads-ի jpg ֆայլերին ըստ անունների"""
import os
from app import app, db, Exhibition

with app.app_context():
    upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    files = os.listdir(upload_dir)
    jpg_files = [f for f in files if f.lower().endswith('.jpg')]
    count = 0
    for ex in Exhibition.query.all():
        # Փնտրում ենք ֆայլ, որի անունը պարունակում է ցուցադրության անունը (հայերեն)
        for fname in jpg_files:
            if ex.title.replace(' ','') in fname.replace(' ',''):
                ex.image_url = fname
                count += 1
                break
    db.session.commit()
    print(f"{count} ցուցադրության նկար կապվեց jpg ֆայլին static/uploads-ում")
