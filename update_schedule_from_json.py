"""
Update schedule.html based on the master sessions.json file
"""

import json
import re
import os
from bs4 import BeautifulSoup

def main():
    print("Updating schedule.html from sessions.json...")
    
    try:
        # Load the sessions.json file
        with open('sessions.json', 'r', encoding='utf-8') as f:
            sessions = json.load(f)
            
        print(f"Loaded {len(sessions)} sessions from sessions.json")
        
        # Group sessions by time slot and location
        schedule = {}
        for session in sessions:
            time_block = session.get('timeBlock', '')
            location = session.get('location', '')
            
            if not time_block or not location:
                continue
                
            if time_block not in schedule:
                schedule[time_block] = {}
                
            # If there's already a session in this location/time slot, skip this one
            # This shouldn't happen with our new ID system, but just in case
            if location in schedule[time_block]:
                print(f"Warning: Multiple sessions scheduled for {location} at {time_block}. Using the first one.")
                continue
                
            schedule[time_block][location] = session
            
        # Load the schedule.html file
        with open('schedule.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the schedule container
        schedule_container = soup.find('div', class_='schedule-container')
        if not schedule_container:
            print("Error: Could not find schedule container in schedule.html")
            return 1
            
        # Clear the existing content
        schedule_container.clear()
        
        # Get the time blocks in order
        time_blocks_order = [
            "8:00 - 9:00",
            "9:00 - 10:00",
            "10:15 - 11:15",
            "11:30 - 12:30",
            "1:30 - 2:30",
            "2:45 - 3:45",
            "3:45 - 4:30"
        ]
        
        # Build the new schedule
        for time_block in time_blocks_order:
            if time_block not in schedule:
                continue
                
            # Create a time block section
            time_section = soup.new_tag('div', attrs={'class': 'time-block'})
            
            # Add time header
            time_header = soup.new_tag('h2')
            time_header.string = time_block
            time_section.append(time_header)
            
            # Create a container for the session cards
            sessions_container = soup.new_tag('div', attrs={'class': 'sessions-container'})
            
            # Get all locations for this time block
            rooms = schedule[time_block].keys()
            
            # Sort rooms in a logical order
            room_order = [
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
            
            sorted_rooms = sorted(rooms, key=lambda x: 
                room_order.index(x) if x in room_order else 999)
            
            # Add a card for each session in this time block
            for room in sorted_rooms:
                session = schedule[time_block][room]
                
                # Create a session card
                card = soup.new_tag('div', attrs={
                    'class': f"session-card {session.get('strand', '')}",
                    'data-strand': session.get('strand', ''),
                    'data-type': session.get('type', '')
                })
                
                # Add room
                room_div = soup.new_tag('div', attrs={'class': 'session-room'})
                room_div.string = room
                card.append(room_div)
                
                # Add title
                title_div = soup.new_tag('div', attrs={'class': 'session-title'})
                title_div.string = session.get('title', '')
                card.append(title_div)
                
                # Add presenter
                presenter = session.get('presenter', '')
                if presenter and not session.get('isSpecialEvent', False):
                    presenter_div = soup.new_tag('div', attrs={'class': 'session-presenter'})
                    presenter_div.string = presenter
                    card.append(presenter_div)
                
                # Add session type badge if not a special event
                if not session.get('isSpecialEvent', False):
                    type_badge = soup.new_tag('div', attrs={'class': 'session-type'})
                    type_badge.string = session.get('typeName', '')
                    card.append(type_badge)
                
                # Add to container
                sessions_container.append(card)
            
            # Add sessions container to time section
            time_section.append(sessions_container)
            
            # Add time section to schedule container
            schedule_container.append(time_section)
        
        # Write the updated HTML back to file
        with open('schedule.html', 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        print("Successfully updated schedule.html")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    main()
