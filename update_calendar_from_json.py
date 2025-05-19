"""
Update calendar.html based on the master sessions.json file
"""

import json
import re
import os
from bs4 import BeautifulSoup

def main():
    print("Updating calendar.html from sessions.json...")
    
    try:
        # Load the sessions.json file
        with open('sessions.json', 'r', encoding='utf-8') as f:
            sessions = json.load(f)
            
        print(f"Loaded {len(sessions)} sessions from sessions.json")
        
        # Group sessions by time slot and location for the calendar view
        calendar_data = {}
        for session in sessions:
            time_block = session.get('timeBlock', '')
            location = session.get('location', '')
            
            if not time_block or not location:
                continue
                
            if time_block not in calendar_data:
                calendar_data[time_block] = {}
                
            calendar_data[time_block][location] = session
        
        # Create a calendar JSON structure for the frontend
        calendar_json = []
        
        # Define the time blocks in order
        time_blocks = [
            "8:00 - 9:00",
            "9:00 - 10:00", 
            "10:15 - 11:15",
            "11:30 - 12:30",
            "1:30 - 2:30",
            "2:45 - 3:45",
            "3:45 - 4:30"
        ]
        
        # Define all possible room columns
        all_rooms = [
            "Hubbard Auditorium",
            "Pearse Hub for Innovation",
            "Brush 2nd Floor",
            "Brush 201",
            "Brush 202",
            "Brush 203",
            "Brush 302",
            "Brush 306",
            "Brush 308", 
            "Brush 310",
            "Brush 314",
            "Writing Center",
            "Kravis Center"
        ]
        
        # Create calendar rows
        for time_slot in time_blocks:
            if time_slot not in calendar_data:
                continue
                
            row = {
                "timeSlot": time_slot,
                "sessions": {}
            }
            
            # Add sessions for each room
            for room in all_rooms:
                if room in calendar_data[time_slot]:
                    session = calendar_data[time_slot][room]
                    row["sessions"][room] = {
                        "id": session.get("id", ""),
                        "title": session.get("title", ""),
                        "presenter": session.get("presenter", ""),
                        "strand": session.get("strand", ""),
                        "type": session.get("type", ""),
                        "isSpecialEvent": session.get("isSpecialEvent", False)
                    }
            
            calendar_json.append(row)
        
        # Create the calendar JSON file
        with open('calendar_data.json', 'w', encoding='utf-8') as f:
            json.dump(calendar_json, f, ensure_ascii=False, indent=2)
            
        # Load the calendar.html file
        with open('calendar.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Update the script that loads calendar data in calendar.html
        updated_content = re.sub(
            r'(const\s+calendarData\s*=\s*).*?(\s*;)',
            r'\1fetch("calendar_data.json").then(response => response.json())\2',
            html_content
        )
        
        # Write the updated HTML back to file
        with open('calendar.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        print("Successfully updated calendar.html and created calendar_data.json")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    main()
