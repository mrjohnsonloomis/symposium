import json

# Load sessions.json
try:
    with open('sessions.json', 'r', encoding='utf-8') as f:
        sessions = json.load(f)
    print(f"Successfully loaded sessions.json with {len(sessions)} sessions")
except Exception as e:
    print(f"Error loading sessions.json: {e}")

# Create a minimal schedule.json
try:
    schedule_data = {
        "timeSlots": [
            {"name": "8:00 - 9:00", "timeRange": "8:00 - 9:00"},
            {"name": "9:00 - 10:00", "timeRange": "9:00 - 10:00"},
            {"name": "10:15 - 11:15", "timeRange": "10:15 - 11:15"},
            {"name": "11:30 - 12:30", "timeRange": "11:30 - 12:30"},
            {"name": "1:30 - 2:30", "timeRange": "1:30 - 2:30"},
            {"name": "2:45 - 3:45", "timeRange": "2:45 - 3:45"},
            {"name": "3:45 - 4:30", "timeRange": "3:45 - 4:30"}
        ],
        "rooms": [
            "Hubbard Auditorium", "Pearse Hub for Innovation", "Brush 2nd Floor", 
            "Brush 201", "Brush 202", "Brush 203", "Brush 302", "Brush 306", 
            "Brush 308", "Brush 310", "Brush 314", "Writing Center", "Kravis Center"
        ],
        "sessions": []
    }
    
    # Convert sessions from sessions.json to schedule.json format
    for session in sessions:
        if not session.get('isSpecialEvent', False):
            schedule_session = {
                'id': session.get('id', ''),
                'title': session.get('title', ''),
                'presenter': session.get('presenter', ''),
                'description': session.get('description', ''),
                'timeSlot': session.get('timeBlock', ''),
                'room': session.get('location', ''),
                'strand': session.get('strand', ''),
                'type': session.get('type', ''),
                'tags': session.get('tags', [])
            }
            schedule_data['sessions'].append(schedule_session)
    
    # Save the schedule.json
    with open('schedule.json', 'w', encoding='utf-8') as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully created schedule.json with {len(schedule_data['sessions'])} sessions")
except Exception as e:
    print(f"Error creating schedule.json: {e}")
