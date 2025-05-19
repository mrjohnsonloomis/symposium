"""
Create schedule.json from sessions.json for backward compatibility
"""

import json
import sys

def main():
    print("Creating schedule.json from sessions.json for backward compatibility...")
    
    try:
        # Load sessions.json
        with open('sessions.json', 'r', encoding='utf-8') as f:
            sessions = json.load(f)
            
        # Extract unique time slots
        time_slots = set()
        rooms = set()
        
        for session in sessions:
            time_block = session.get('timeBlock', '')
            location = session.get('location', '')
            if time_block:
                time_slots.add(time_block)
            if location:
                rooms.add(location)
        
        # Convert to the schedule.json format
        schedule_data = {
            'timeSlots': [
                {'name': time_slot, 'timeRange': time_slot}
                for time_slot in sorted(list(time_slots))
            ],
            'rooms': sorted(list(rooms)),
            'sessions': []
        }
        
        # Add sessions
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
                    'strandName': session.get('strandName', ''),
                    'type': session.get('type', ''),
                    'typeName': session.get('typeName', ''),
                    'tags': session.get('tags', [])
                }
                schedule_data['sessions'].append(schedule_session)
        
        # Write schedule.json
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully created schedule.json with {len(schedule_data['sessions'])} sessions")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
