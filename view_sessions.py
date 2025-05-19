import json

with open('sessions.json') as f:
    data = json.load(f)

print(f'Total sessions: {len(data)}')
print('Sample entry:')
print(json.dumps(data[0], indent=2))
