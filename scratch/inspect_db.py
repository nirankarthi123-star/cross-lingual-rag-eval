import sqlite3
conn = sqlite3.connect('data/rag_eval.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('TABLES:', tables)

for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'  {t}: {cur.fetchone()[0]} rows')

cur.execute('SELECT question_id, language, mitigation_enabled, faithfulness_score, hallucination_flag FROM experiment_results LIMIT 25')
rows = cur.fetchall()
print('\nSAMPLE EXPERIMENT RESULTS:')
for r in rows:
    print(dict(r))

conn.close()
