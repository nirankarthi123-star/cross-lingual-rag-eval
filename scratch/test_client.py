import sys
sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

queries = [
    ('Tanglish Broadband Cancel', 'Broadband connection cancel panna evlo days notice kudukanum?', True),
    ('Tanglish 5G SIM', '5G network use panna new SIM card venuma?', True),
    ('English Broadband', 'How many days notice should I give to cancel my broadband connection?', True),
]

for label, q, mitigation in queries:
    print(f'=== {label} ===')
    r = client.post('/api/chat', json={'query': q, 'mitigation_enabled': mitigation})
    if r.status_code != 200:
        print(f'  ERROR {r.status_code}: {r.text}')
        print()
        continue
    
    d = r.json()
    print(f'  code_mix_detected: {d.get("code_mix_detected")}')
    print(f'  detected_languages: {d.get("detected_languages")}')
    print(f'  mitigation_applied: {d.get("mitigation_applied")}')
    norm = d.get("normalized_query")
    print(f'  normalized_query: {norm if norm else "(not applied)"}')
    print(f'  faithfulness_score: {d.get("faithfulness_score")}')
    print()
