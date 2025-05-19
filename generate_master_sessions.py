"""
Generate master sessions.json from sessions.csv and schedule_by_id.xlsx

This script combines session details from sessions.csv with room and time assignments
from schedule_by_id.xlsx to create a comprehensive sessions.json file.
"""

import pandas as pd
import numpy as np
import json
import html
import re
import os
import sys

def html_encode_but_preserve_quotes(text):
    """HTML escapes text but converts quote HTML entities back to actual quotes"""
    if not text:
        return ""
    escaped = html.escape(str(text))
    return escaped.replace("&quot;", "\"").replace("&#x27;", "'")

def extract_tags(text):
    """Extract tags from a text field"""
    if pd.isna(text):
        return []
    
    # If the field already contains a comma-separated list, split it
    if isinstance(text, str) and ',' in text:
        return [tag.strip() for tag in text.split(',') if tag.strip()]
    
    return []

def get_time_for_slot(slot_name):
    """Convert slot name to actual time range"""
    slot_map = {
        "Slot 1 (10:15-11:15)": "10:15 - 11:15",
        "Slot 2 (11:30-12:30)": "11:30 - 12:30",
        "Slot 3 (1:30-2:30)": "1:30 - 2:30",
        "Slot 4 (2:45-3:45)": "2:45 - 3:45",
        "8:00-9:00": "8:00 - 9:00",
        "9:00-10:00": "9:00 - 10:00",
        "3:45-4:30": "3:45 - 4:30"
    }
    return slot_map.get(slot_name, slot_name)

def get_strand_name(strand_number):
    """Get the full strand name based on the strand number"""
    strand_names = {
        "1": "1: AI in the Classroom",
        "2": "2: Human-Centered Innovation",
        "3": "3: Preparing for the Changing Workforce",
        "4": "4: Ethics & Creative Rights"
    }
    return strand_names.get(strand_number, f"{strand_number}: Unknown Strand")

def get_type_name(session_type):
    """Get the full session type name"""
    type_names = {
        "Workshop": "Workshop",
        "Presentation": "Presentation",
        "Panel": "Panel",
        "Special": "Special Event"
    }
    return type_names.get(session_type, session_type)

def get_preview(description, max_length=150):
    """Generate a preview of the description"""
    if pd.isna(description):
        return ""
    
    # Strip any HTML tags
    text = re.sub(r'<[^>]+>', '', str(description))
    
    # Truncate to max_length
    if len(text) > max_length:
        # Try to truncate at a sentence or period
        last_period = text[:max_length].rfind('.')
        if last_period > max_length * 0.5:  # Only use period if it's not too short
            return text[:last_period+1]
        
        # Otherwise truncate at a word boundary
        last_space = text[:max_length].rfind(' ')
        return text[:last_space] + "..."
    
    return text

def main():
    print("Processing session data...")
    
    try:
        # Read the input files with explicit encoding handling
        sessions_csv = pd.read_csv('sessions.csv', encoding='utf-8', engine='python')
        schedule_excel = pd.read_excel('schedule_by_id.xlsx')
        
        # Check if files were read correctly
        print(f"Read {len(sessions_csv)} sessions from CSV")
        print(f"Read {len(schedule_excel)} schedule rows from Excel")
        
        # Create a mapping of session IDs to room and time slot
        session_schedule = {}
        
        # Create a list to store special events (non-session entries)
        special_events = []
        
        # Process the schedule Excel file
        for _, row in schedule_excel.iterrows():
            time_slot = row['Time Slot']
            
            # Skip rows without a time slot
            if pd.isna(time_slot):
                continue
                
            # Process each room column
            for room in schedule_excel.columns[1:]:  # Skip the Time Slot column
                cell_value = row[room]
                
                # Skip empty cells
                if pd.isna(cell_value):
                    continue
                    
                # Try to convert to integer if it's a session ID
                try:
                    session_id = int(cell_value)
                    # Modified to support multiple time slots for the same session
                    if session_id not in session_schedule:
                        session_schedule[session_id] = []
                    
                    # Add this time slot and room to the session's schedule
                    session_schedule[session_id].append({
                        'location': room,
                        'timeBlock': get_time_for_slot(time_slot)
                    })
                except (ValueError, TypeError):
                    # This is a special event, not a session ID
                    special_events.append({
                        'title': str(cell_value),
                        'location': room,
                        'timeBlock': get_time_for_slot(time_slot),
                        'isSpecialEvent': True
                    })
        
        # Create the sessions JSON structure
        sessions_json = []
        
        # First, process regular sessions from CSV
        for _, row in sessions_csv.iterrows():
            # Skip header rows or empty rows
            if pd.isna(row.get('sessionID')) or not str(row.get('sessionID')).isdigit():
                continue
                
            session_id = int(row['sessionID'])
            
            # Get strand number from "Which strand will your presentation be in?" column
            strand_text = row.get('Which strand will your presentation be in?', '')
            strand_number = '0'
            
            if isinstance(strand_text, str) and 'Strand' in strand_text:
                match = re.search(r'Strand\s+(\d+)', strand_text)
                if match:
                    strand_number = match.group(1)
            
            # Extract session type
            session_type = row.get('What is the format of your session?', 'Workshop')
            
            # Extract tags - handle column name with potential newline
            tags_column = 'Tags\n' if 'Tags\n' in row.index else 'Tags'
            tags_field = row.get(tags_column, '')
            tags = extract_tags(tags_field)
            
            # Create session object
            session = {
                'id': session_id,
                'strand': f'strand{strand_number}',
                'strandName': get_strand_name(strand_number),
                'type': session_type.lower() if not pd.isna(session_type) else 'workshop',
                'typeName': get_type_name(session_type),
                'title': html_encode_but_preserve_quotes(row.get('Session Title', '')),
                'presenter': html_encode_but_preserve_quotes(row.get('Name2', '')),
                'email': row.get('E-mail address', ''),
                'organization': row.get('School or Organization', ''),
                'description': html_encode_but_preserve_quotes(row.get('Session Description', '')),
                'timeBlock': '',  # Will be populated from schedule
                'location': '',   # Will be populated from schedule
                'tags': tags,
                'isSpecialEvent': False
            }
            
            # Add preview field
            session['preview'] = get_preview(session['description'])
            
            # Add room and time information if available
            if session_id in session_schedule:
                # Support for multiple time slots
                session_occurrences = session_schedule[session_id]
                
                if len(session_occurrences) == 1:
                    # If session occurs only once, keep the original structure
                    session['timeBlock'] = session_occurrences[0]['timeBlock']
                    session['location'] = session_occurrences[0]['location']
                    sessions_json.append(session)
                else:
                    # If session occurs multiple times, create a separate entry for each occurrence
                    for i, occurrence in enumerate(session_occurrences):
                        # For the first occurrence, modify the existing session object
                        if i == 0:
                            session['timeBlock'] = occurrence['timeBlock']
                            session['location'] = occurrence['location']
                            sessions_json.append(session)
                        else:
                            # For additional occurrences, create a copy with a new ID
                            new_session = session.copy()
                            new_session['id'] = f"{session_id}_occurrence_{i+1}"
                            new_session['timeBlock'] = occurrence['timeBlock']
                            new_session['location'] = occurrence['location']
                            sessions_json.append(new_session)
            else:
                # Session has no schedule information
                sessions_json.append(session)
            
        # Then, add special events
        for event in special_events:
            
            # Create a special event session
            session = {
                'id': f"special_{len(sessions_json) + 1}",  # Generate a unique ID
                'strand': 'special',
                'strandName': 'Special Event',
                'type': 'special',
                'typeName': 'Special Event',
                'title': event['title'],
                'presenter': '',
                'email': '',
                'organization': '',
                'description': f"Special event: {event['title']}",
                'preview': f"Special event: {event['title']}",
                'timeBlock': event['timeBlock'],
                'location': event['location'],
                'tags': ['Special Event'],
                'isSpecialEvent': True
            }
            
            sessions_json.append(session)
        
        # Check for sessions in CSV that are not in the schedule
        unscheduled_sessions = [s['id'] for s in sessions_json if not s['timeBlock']]
        if unscheduled_sessions:
            print(f"Warning: {len(unscheduled_sessions)} sessions are not scheduled:")
            for session_id in unscheduled_sessions[:5]:  # Show first 5
                session = next((s for s in sessions_json if s['id'] == session_id), None)
                if session:
                    print(f"  ID: {session_id}, Title: {session['title']}")
            if len(unscheduled_sessions) > 5:
                print(f"  ... and {len(unscheduled_sessions) - 5} more")
        
        # Check for sessions in the schedule that are not in the CSV
        all_session_ids = set(int(row['sessionID']) for _, row in sessions_csv.iterrows() 
                             if not pd.isna(row.get('sessionID')) and str(row.get('sessionID')).isdigit())
        scheduled_ids = set(session_schedule.keys())
        unknown_schedule_ids = scheduled_ids - all_session_ids
        
        if unknown_schedule_ids:
            print(f"Warning: {len(unknown_schedule_ids)} schedule entries have IDs not in the sessions CSV:")
            for session_id in list(unknown_schedule_ids)[:5]:  # Show first 5
                location = session_schedule[session_id]['location']
                time = session_schedule[session_id]['timeBlock']
                print(f"  ID: {session_id}, Location: {location}, Time: {time}")
            if len(unknown_schedule_ids) > 5:
                print(f"  ... and {len(unknown_schedule_ids) - 5} more")
        
        # Write the output JSON
        with open('sessions.json', 'w', encoding='utf-8') as f:
            json.dump(sessions_json, f, ensure_ascii=False, indent=2)
            
        print(f"\nSuccessfully wrote {len(sessions_json)} sessions to sessions.json")
        
        # Count statistics
        regular_sessions = sum(1 for s in sessions_json if not s.get('isSpecialEvent', False))
        special_sessions = sum(1 for s in sessions_json if s.get('isSpecialEvent', False))
        scheduled_sessions = sum(1 for s in sessions_json if s.get('timeBlock') and s.get('location'))
        unscheduled_sessions = sum(1 for s in sessions_json if not s.get('timeBlock') or not s.get('location'))
        
        print(f"\nSummary:")
        print(f"- Regular sessions: {regular_sessions}")
        print(f"- Special events: {special_sessions}")
        print(f"- Scheduled sessions: {scheduled_sessions}")
        print(f"- Unscheduled sessions: {unscheduled_sessions}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
