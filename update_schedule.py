"""
This script updates the schedule.json file based on the session_schedule_by_slot.xlsx file
"""

import pandas as pd
import json
import os
import re

def find_session_by_title(sessions, title):
    """Find a session in the sessions list by title (or partial title match)"""
    # Remove any presenter or custom notation from the title
    clean_title = re.sub(r'(.+?):\s*', '', title).strip()
    
    # First try exact match
    for session in sessions:
        if session.get('title') == clean_title:
            return session
    
    # Then try partial match (title might be truncated in Excel)
    for session in sessions:
        session_title = session.get('title', '')
        if clean_title and session_title and (clean_title in session_title or session_title in clean_title):
            return session
    
    # If no match, return a placeholder
    return {
        "title": clean_title if clean_title else title,
        "presenter": "",
        "description": "Session details not available.",
        "strand": "",
        "type": "",
        "typeName": "",
        "tags": []
    }

def excel_to_schedule_json(excel_file, sessions_json_file, output_file='schedule.json'):
    """
    Convert Excel schedule to JSON for calendar view
    
    Args:
        excel_file: Path to Excel file with schedule
        sessions_json_file: Path to sessions.json for detailed info
        output_file: Output JSON file
    """
    try:
        # Load Excel file
        df = pd.read_excel(excel_file)
        
        # Load sessions data
        with open(sessions_json_file, 'r') as f:
            sessions_data = json.load(f)
        
        # Create schedule structure
        schedule = {
            "timeSlots": [],
            "rooms": df.columns[1:].tolist(),  # Skip the first column (Time Slot)
            "sessions": []
        }
        
        # Process each row (time slot)
        for _, row in df.iterrows():
            time_slot = row['Time Slot']
            
            # Extract time range from slot name, e.g., "Slot 1 (10:15-11:15)" -> "10:15-11:15"
            time_range = re.search(r'\((.*?)\)', time_slot)
            time_range = time_range.group(1) if time_range else time_slot
            
            # Add time slot to list
            schedule["timeSlots"].append({
                "name": time_slot,
                "timeRange": time_range
            })
            
            # Process sessions in this time slot
            for room in df.columns[1:]:  # Skip the first column (Time Slot)
                session_title = row[room]
                
                # Skip empty cells
                if pd.isna(session_title) or session_title == '':
                    continue
                
                # Find session details
                session_details = find_session_by_title(sessions_data, session_title)
                
                # Add session to schedule
                schedule["sessions"].append({
                    "timeSlot": time_slot,
                    "room": room,
                    "sessionId": session_details.get("id", ""),
                    "title": session_details.get("title", session_title),
                    "presenter": session_details.get("presenter", ""),
                    "description": session_details.get("description", ""),
                    "strand": session_details.get("strand", ""),
                    "strandName": session_details.get("strandName", ""),
                    "type": session_details.get("type", ""),
                    "typeName": session_details.get("typeName", ""),
                    "tags": session_details.get("tags", [])
                })
        
        # Write schedule to JSON file
        with open(output_file, 'w') as f:
            json.dump(schedule, f, indent=2)
        
        print(f"Schedule successfully converted to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error converting schedule: {e}")
        return False

if __name__ == "__main__":
    excel_file = 'session_schedule_by_slot.xlsx'
    sessions_json_file = 'sessions.json'
    output_file = 'schedule.json'
    
    print(f"Converting {excel_file} to {output_file}...")
    excel_to_schedule_json(excel_file, sessions_json_file, output_file)
