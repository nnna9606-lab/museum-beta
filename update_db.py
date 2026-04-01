import sqlite3

def add_image_columns():
    """Add image_url, thumbnail_url, category and tags columns to artifact table if missing"""
    conn = sqlite3.connect('instance/museum.db')
    c = conn.cursor()

    # Helper to add a column if it doesn't exist
    def add_column(sql):
        try:
            c.execute(sql)
            print(f"Executed: {sql}")
        except sqlite3.OperationalError as e:
            # SQLite raises OperationalError if column already exists
            print(f"Skipped (likely exists): {sql} -> {e}")

    add_column("ALTER TABLE artifact ADD COLUMN image_url TEXT")
    add_column("ALTER TABLE artifact ADD COLUMN thumbnail_url TEXT")
    add_column("ALTER TABLE artifact ADD COLUMN category TEXT")
    add_column("ALTER TABLE artifact ADD COLUMN tags TEXT")
    add_column("ALTER TABLE user ADD COLUMN profile_image TEXT")
    # Add created_at and updated_at columns (no non-constant defaults on ALTER TABLE)
    add_column("ALTER TABLE artifact ADD COLUMN created_at DATETIME")
    add_column("ALTER TABLE artifact ADD COLUMN updated_at DATETIME")

    # Populate existing rows with current timestamp where NULL
    try:
        c.execute("UPDATE artifact SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        c.execute("UPDATE artifact SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        print("Populated created_at/updated_at for existing rows")
    except sqlite3.OperationalError as e:
        print(f"Could not populate timestamps: {e}")

    conn.commit()
    conn.close()
    print("Database update finished.")

if __name__ == '__main__':
    add_image_columns()