import sqlite3
conn = sqlite3.connect('data/rag_eval.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check evaluations table (the 18 rows from the pilot)
cur.execute("SELECT * FROM evaluations LIMIT 30")
rows = cur.fetchall()
print('EVALUATIONS TABLE (pilot results):')
if rows:
    print('Columns:', list(rows[0].keys()))
    for r in rows:
        print(dict(r))
else:
    print('(empty)')

print()

# Check experiment_configs
cur.execute("SELECT * FROM experiment_configs")
rows = cur.fetchall()
print('EXPERIMENT_CONFIGS:')
if rows:
    print('Columns:', list(rows[0].keys()))
    for r in rows:
        print(dict(r))
else:
    print('(empty)')

conn.close()
