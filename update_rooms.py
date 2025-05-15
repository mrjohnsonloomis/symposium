import json
import re

def normalize_title(title):
    """
    Normalize session titles by converting HTML entities and handling different quote types
    """
    if not title:
        return ""
    # Replace HTML entities and normalize quotes
    normalized = (title.replace('&quot;', '"')
                      .replace('&#x27;', "'")
                      .replace('"', '"')
                      .replace('"', '"'))
    return normalized

def find_session_by_title(sessions, schedule_title):
    """
    Find a session by title, accounting for variations in formatting
    """
    # Handle special events
    if isinstance(schedule_title, str) and ("arrival" in schedule_title.lower() or 
                                            "keynote" in schedule_title.lower() or 
                                            "closing" in schedule_title.lower()):
        # These don't need to be matched against regular sessions
        return None
        
    # Remove any presenter prefix (e.g., "Cotton: ")
    clean_title = re.sub(r'(.+?):\s*', '', schedule_title).strip() if isinstance(schedule_title, str) else ""
    normalized_schedule_title = normalize_title(clean_title)
    
    # First try exact match with normalized titles
    for session in sessions:
        session_title = session.get('title', '')
        normalized_session_title = normalize_title(session_title)
        
        if normalized_session_title == normalized_schedule_title:
            return session
    
    # Then try partial match
    for session in sessions:
        session_title = session.get('title', '')
        normalized_session_title = normalize_title(session_title)
        
        if (normalized_schedule_title and normalized_session_title and 
            (normalized_schedule_title in normalized_session_title or 
             normalized_session_title in normalized_schedule_title)):
            return session
    
    return None

def update_calendar_with_rooms():
    """
    Update the calendar data with room assignments from schedule.json
    """
    try:
        # Load schedule data
        with open('schedule.json', 'r') as f:
            schedule_data = json.load(f)
        
        # Create mapping of session title to room and time slot
        session_info = {}
        for session in schedule_data['sessions']:
            title = session.get('title', '')
            room = session.get('room', '')
            time_slot = session.get('timeSlot', '')
            
            if title and room:
                # Handle duplicate sessions (same session in multiple time slots)
                if title in session_info:
                    # If we already have this session, append the time slot
                    existing_room = session_info[title]['room']
                    existing_time = session_info[title]['time_slot']
                    
                    # If rooms match, just update the time slot
                    if existing_room == room:
                        # Only append if it's a different time slot
                        if time_slot != existing_time and time_slot not in existing_time:
                            session_info[title]['time_slot'] = f"{existing_time} and {time_slot}"
                    else:
                        # If rooms don't match, specify room per time slot
                        combined_info = f"{existing_time} in {existing_room} and {time_slot} in {room}"
                        session_info[title] = {
                            'room': f"{existing_room}/{room}",
                            'time_slot': combined_info
                        }
                else:
                    session_info[title] = {
                        'room': room,
                        'time_slot': time_slot
                    }
        
        # Load session data
        with open('sessions.json', 'r') as f:
            sessions_data = json.load(f)
        
        # Update session locations
        updated_count = 0
        special_cases = ["Student Buy-In", "Deeper Dive"]
        
        for session in sessions_data:
            session_title = session.get('title', '')
            normalized_title = normalize_title(session_title)
            
            # Handle special cases by name
            special_case = False
            for case in special_cases:
                if case in session_title:
                    special_case = True
                    break
            
            # Skip sessions that already have locations and aren't special cases
            if session.get('location') and not special_case:
                continue
                
            # Check for special venues for keynote, arrival, etc.
            if "keynote" in session_title.lower() or "arrival" in session_title.lower() or "closing" in session_title.lower():
                session['location'] = "Hubbard Auditorium"
                updated_count += 1
                continue
                
            # Direct lookup by title
            if normalized_title in session_info:
                session['location'] = session_info[normalized_title]['room']
                if session.get('timeBlock') == 'TBD':
                    session['timeBlock'] = session_info[normalized_title]['time_slot']
                updated_count += 1
                continue
            
            # Fuzzy matching for harder-to-match titles
            found_session = False
            for schedule_title, info in session_info.items():
                normalized_schedule_title = normalize_title(schedule_title)
                if (normalized_title and normalized_schedule_title and
                    (normalized_title in normalized_schedule_title or 
                     normalized_schedule_title in normalized_title)):
                    session['location'] = info['room']
                    if session.get('timeBlock') == 'TBD':
                        session['timeBlock'] = info['time_slot']
                    updated_count += 1
                    found_session = True
                    break
            
            if not found_session and special_case:
                # Handle known special cases
                if "Student Buy-In" in session_title and "Ungrading" in session_title:
                    session['location'] = "Room G"
                    session['timeBlock'] = "Slot 1 (10:15-11:15) and Slot 2 (11:30-12:30)"
                    updated_count += 1
                elif "Deeper Dive" in session_title:
                    session['location'] = "Room A"
                    session['timeBlock'] = "Slot 1 (10:15-11:15)"
                    updated_count += 1
        
        # Save updated sessions data
        with open('sessions.json', 'w') as f:
            json.dump(sessions_data, f, indent=2)
        
        print(f"Updated {updated_count} sessions with room assignments.")
        return True
        
    except Exception as e:
        print(f"Error updating calendar with rooms: {e}")
        return False

if __name__ == "__main__":
    print("Updating sessions with room assignments...")
    update_calendar_with_rooms()
