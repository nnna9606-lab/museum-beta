"""Add image fields to Artifact table

This migration adds image_url and thumbnail_url fields to the Artifact table.
"""
from app import db

def upgrade():
    # Get database connection
    conn = db.engine.connect()
    
    # Add new columns
    conn.execute('ALTER TABLE artifact ADD COLUMN image_url TEXT')
    conn.execute('ALTER TABLE artifact ADD COLUMN thumbnail_url TEXT')
    
    # Commit the transaction
    conn.commit()

def downgrade():
    # Get database connection
    conn = db.engine.connect()
    
    # Remove columns
    conn.execute('ALTER TABLE artifact DROP COLUMN thumbnail_url')
    conn.execute('ALTER TABLE artifact DROP COLUMN image_url')
    
    # Commit the transaction
    conn.commit()

if __name__ == '__main__':
    upgrade()