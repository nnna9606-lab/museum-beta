#!/usr/bin/env python3
"""Փոխում է Հնագույն Պղնձե Զանգ նմուշի նկարը, որ ցույց տա Հնագույնզանգ․jpg"""
from app import app, db, Artifact

with app.app_context():
    # Գտնել "Հնագույն Պղնձե Զանգ" նմուշը
    artifact = Artifact.query.filter(Artifact.name == "Հնագույն Պղնձե Զանգ").first()
    if artifact:
        artifact.image_url = "Հնագույնզանգ․jpg"
        db.session.commit()
        print("Նկարը հաջողությամբ փոխվեց։")
    else:
        print("Նմուշը չի գտնվել։")
