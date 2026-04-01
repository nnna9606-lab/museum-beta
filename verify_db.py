#!/usr/bin/env python3
"""Quick database verification"""
from app import app, db, Artifact, Exhibition, ArtifactImage

with app.app_context():
    print("📊 DATABASE VERIFICATION\n" + "="*50)
    
    print("\n🏺 ARTIFACTS:")
    artifacts = Artifact.query.all()
    for i, artifact in enumerate(artifacts, 1):
        images = ArtifactImage.query.filter_by(artifact_id=artifact.id).count()
        print(f"\n  {i}. {artifact.name}")
        print(f"     • Year: {artifact.year}")
        print(f"     • Category: {artifact.category}")
        print(f"     • Main image: {artifact.image_url}")
        print(f"     • Additional images: {images}")
        print(f"     • Description: {artifact.description[:50]}...")
    
    print("\n\n🎭 EXHIBITIONS:")
    exhibitions = Exhibition.query.all()
    for i, ex in enumerate(exhibitions, 1):
        print(f"\n  {i}. {ex.title}")
        print(f"     • Dates: {ex.start_date} to {ex.end_date}")
        print(f"     • Image: {ex.image_url}")
        print(f"     • Artifacts in exhibition: {len(ex.artifacts)}")
        if ex.artifacts:
            for artifact in ex.artifacts:
                print(f"       - {artifact.name}")
    
    print("\n\n📸 IMAGE COUNT:")
    total_images = ArtifactImage.query.count()
    print(f"  Total artifact images in DB: {total_images}")
    
    print("\n" + "="*50)
    print("✅ Verification complete!")
