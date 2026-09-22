import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('data/rag_eval.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Evaluations table summary
cur.execute("SELECT COUNT(*), AVG(faithfulness_score), MIN(faithfulness_score), MAX(faithfulness_score), SUM(hallucination_flag) FROM evaluations")
r = cur.fetchone()
print('EVALUATIONS SUMMARY:')
print(f'  Count: {r[0]}, Avg score: {r[1]}, Min: {r[2]}, Max: {r[3]}, Hallucinations: {r[4]}')

cur.execute("SELECT faithfulness_score, hallucination_flag, judge_model FROM evaluations LIMIT 5")
rows = cur.fetchall()
print('First 5 evaluations:')
for row in rows:
    print(f'  score={row[0]}, hallucination={row[1]}, judge={row[2]}')

# Experiment results
cur.execute("SELECT COUNT(*) FROM experiment_results")
print(f'\nExperiment results total: {cur.fetchone()[0]}')
cur.execute("SELECT COUNT(*) FROM experiment_results WHERE faithfulness_score IS NOT NULL")
print(f'Experiment results with faithfulness_score: {cur.fetchone()[0]}')

# Configs
print('\nExperiment configs:')
cur.execute("SELECT * FROM experiment_configs")
for r in cur.fetchall():
    print(dict(r))

conn.close()
