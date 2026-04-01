"""
Migration: Add translation columns to Artifact and Exhibition tables
Adds support for Armenian (hy), Russian (ru), and English (en) translations
"""
import sqlite3
import os

def add_translation_columns():
    """Add translation columns to artifact and exhibition tables"""
    db_path = 'instance/museum.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Add columns to artifact table
        print("Adding translation columns to artifact table...")
        columns_to_add = [
            "ALTER TABLE artifact ADD COLUMN name_ru TEXT",
            "ALTER TABLE artifact ADD COLUMN name_en TEXT",
            "ALTER TABLE artifact ADD COLUMN description_ru TEXT",
            "ALTER TABLE artifact ADD COLUMN description_en TEXT",
        ]
        
        for sql in columns_to_add:
            try:
                c.execute(sql)
                print(f"✓ Executed: {sql}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"✓ Column already exists (skipped): {sql}")
                else:
                    print(f"✗ Error: {e}")
        
        # Add columns to exhibition table
        print("\nAdding translation columns to exhibition table...")
        exhibition_columns = [
            "ALTER TABLE exhibition ADD COLUMN title_ru TEXT",
            "ALTER TABLE exhibition ADD COLUMN title_en TEXT",
            "ALTER TABLE exhibition ADD COLUMN description_ru TEXT",
            "ALTER TABLE exhibition ADD COLUMN description_en TEXT",
        ]
        
        for sql in exhibition_columns:
            try:
                c.execute(sql)
                print(f"✓ Executed: {sql}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"✓ Column already exists (skipped): {sql}")
                else:
                    print(f"✗ Error: {e}")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    add_translation_columns()
