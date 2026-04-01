import sqlite3

conn = sqlite3.connect('instance/museum.db')
c = conn.cursor()

c.execute("PRAGMA table_info('artifact')")
cols = c.fetchall()
print('artifact table columns:')
for col in cols:
    # PRAGMA table_info returns (cid, name, type, notnull, dflt_value, pk)
    print(f"- {col[1]} ({col[2]})")

conn.close()