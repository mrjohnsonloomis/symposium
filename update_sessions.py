import json

# Load sessions data
with open('sessions.json', 'r') as f:
    sessions = json.load(f)

# Update session information
for session in sessions:
    title = session.get('title', '')
    if '&quot;Ungrading&quot;' in title:
        session['timeBlock'] = 'Slot 1 (10:15-11:15) and Slot 2 (11:30-12:30)'
        session['location'] = 'Room G'
        print(f"Updated session: {title}")
    elif 'Deeper Dive' in title or 'Extended Mind' in title:
        session['timeBlock'] = 'Slot 1 (10:15-11:15)'
        session['location'] = 'Room A'
        print(f"Updated session: {title}")

# Save updated sessions data
with open('sessions.json', 'w') as f:
    json.dump(sessions, f, indent=2)

print('Sessions updated successfully.')
