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

def fix_common_mojibake(text):
    """Fix common mojibake patterns in text."""
    if not isinstance(text, str):
        return text

    # Order of replacements can matter if one mojibake is a substring of another,
    # but for these specific patterns, it should be fine.
    # More complex (double-encoded) mojibakes first
    text = text.replace("Ã¢â¬â¢", "’")  # U+2019 RIGHT SINGLE QUOTATION MARK
    text = text.replace("Ã¢â¬Ëœ", "‘")  # U+2018 LEFT SINGLE QUOTATION MARK
    text = text.replace("Ã¢â¬Â", "”")  # U+201D RIGHT DOUBLE QUOTATION MARK (corrected from Âť)
    text = text.replace("Ã¢â¬Å“", "“")  # U+201C LEFT DOUBLE QUOTATION MARK
    text = text.replace("Ã¢â¬â", "–")  # U+2013 EN DASH
    text = text.replace("Ã¢â¬â", "—")  # U+2014 EM DASH
    text = text.replace("Ã¢â¬Â¦", "…")  # U+2026 HORIZONTAL ELLIPSIS
    
    # Simpler mojibakes (UTF-8 bytes misread as single-byte encoding)
    text = text.replace("â€™", "’")
    text = text.replace("â€˜", "‘")
    text = text.replace("â€", "”") # Common for right double quote
    text = text.replace("â€ś", "“") # Common for left double quote
    text = text.replace("â€“", "–")
    text = text.replace("â€”", "—")
    text = text.replace("â€¦", "…")
    text = text.replace("â‚¬", "€") # Euro sign, just in case

    # Special case for "Ő" and "Ń" from user's calendar.html example if they appear mangled
    # Example: If "Ő" (U+0150) became "Å" (UTF-8 bytes C5 90 misread as latin1/cp1252)
    text = text.replace("Å", "Ő") 
    # Example: If "Ń" (U+0143) became "Å" (UTF-8 bytes C5 83 misread as latin1/cp1252)
    text = text.replace("Å", "Ń")

    return text

def normalize_session_type(raw_type_string):
    if pd.isna(raw_type_string) or not isinstance(raw_type_string, str):
        return "default"
    
    s_type = str(raw_type_string).strip().lower()

    if not s_type: # Handle empty string after strip
        return "default"

    # Order can be important here. More specific checks first.
    # Checking for more complex/longer strings first
    if "presentation but then participate in our learning lab protocol" in s_type:
        return "presentation"
    if "a combination - some presentation, and some chances for participants to engage" in s_type:
        return "workshop"
    if "a combination of a workshop and facilitated dicussion" in s_type: # Typo "dicussion" might be in source data
        return "workshop" 
    if "presentation with q&a and application activity" in s_type:
        return "presentation"
    if "presentation and q&a" in s_type:
        return "presentation"
    if "facilitated discussion" in s_type:
        return "discussion"

    # Simpler keyword checks
    if "workshop" in s_type:
        return "workshop"
    if "presentation" in s_type: # Catches "presentation" if not caught by more specific above
        return "presentation"
    if "discussion" in s_type: # Catches "discussion" if not caught by "facilitated discussion"
        return "discussion"
    if "panel" in s_type:
        return "panel"
    if "keynote" in s_type: # Usually handled by isSpecialEvent, but good to have
        return "keynote" 
    
    # If no keywords matched, return "default"
    # print(f"Info: Session type '{raw_type_string}' normalized to 'default'")
    return "default"

def html_encode_but_preserve_quotes(text):
    """HTML escapes text but converts quote HTML entities back to actual quotes"""
    if pd.isna(text) or text is None: # Added check for None
        return ""
    escaped = html.escape(str(text)) # Ensure text is string
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
    if pd.isna(description) or description is None: # Added check for None
        return ""
    
    # Description is already mojibake-fixed and HTML-encoded by the time it's stored in session['description']
    # For preview, we want to strip HTML that might have been in the original or added by html_encode_but_preserve_quotes
    # However, html_encode_but_preserve_quotes primarily escapes &, <, >.
    # The original get_preview strips tags like <p>, <b> etc.
    # Let's assume session['description'] (passed as 'description' arg here) has had mojibake fixed,
    # and then html_encode_but_preserve_quotes applied.
    # We need to unescape basic entities for preview if html_encode_but_preserve_quotes was aggressive,
    # but it's not. It preserves quotes.
    # The main task for get_preview is stripping structural HTML and truncating.

    text_to_preview = str(description) # Ensure it's a string

    # Strip any HTML tags that might be present (e.g. if original CSV had them)
    text_to_preview = re.sub(r'<[^>]+>', '', text_to_preview)
    
    # Truncate to max_length
    if len(text_to_preview) > max_length:
        # Try to truncate at a sentence or period
        last_period = text_to_preview[:max_length].rfind('.')
        if last_period > max_length * 0.5:  # Only use period if it's not too short
            return text_to_preview[:last_period+1]
        
        # Otherwise truncate at a word boundary
        last_space = text_to_preview[:max_length].rfind(' ')
        if last_space != -1: # Check if space was found
            return text_to_preview[:last_space] + "..."
        else: # No space found, just truncate
            return text_to_preview[:max_length] + "..."
    
    return text_to_preview

def main():
    print("Processing session data...")
    
    try:
        # Read the input files with explicit encoding handling
        # Try 'latin1' (ISO-8859-1) as another common encoding that might handle the problematic characters.
        sessions_csv = pd.read_csv('sessions.csv', encoding='utf-8', on_bad_lines='skip')
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
                    if session_id not in session_schedule:
                        session_schedule[session_id] = []
                    
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
            strand_number = '0' # Default if not found
            
            if isinstance(strand_text, str) and 'Strand' in strand_text:
                match = re.search(r'Strand\s+(\d+)', strand_text) # Changed to raw string
                if match:
                    strand_number = match.group(1)
            
            # DEBUG: Print session ID and extracted strand number
            # print(f"Processing Session ID: {session_id}, Extracted Strand: {strand_number}")

            # MODIFICATION: Filter for Strand 1 and Strand 2 only
            if strand_number not in ['1', '2']:
                # print(f"Skipping session ID {session_id} (Title: {row.get('Session Title', '')}) due to strand: {strand_number}")
                continue
            
            # Extract session type
            session_type = row.get('What is the format of your session?', 'Workshop')
            
            # Extract tags - handle column name with potential newline
            tags_column = 'Tags\\n' if 'Tags\\n' in row.index else 'Tags'
            tags_field = row.get(tags_column, '')
            tags = extract_tags(tags_field)
            
            # Create session object
            session = {
                'id': session_id,
                'strand': f'strand{strand_number}',
                'strandName': get_strand_name(strand_number),
                'tags': tags,
                'isSpecialEvent': False,
                'occurrences': [] # Initialize occurrences array
            }

            # Populate fields, converting NaN to None for JSON compatibility
            
            # Session Type
            _raw_session_type_for_type = row.get('What is the format of your session?')
            session['type'] = normalize_session_type(_raw_session_type_for_type) # MODIFIED to use normalize_session_type
            
            _raw_session_type_for_typeName = row.get('What is the format of your session?', 'Workshop')
            session['typeName'] = get_type_name(str(_raw_session_type_for_typeName) if pd.notna(_raw_session_type_for_typeName) else 'Workshop')

            # Title
            _title_val = row.get('Session Title')
            _title_val = fix_common_mojibake(str(_title_val)) if pd.notna(_title_val) else None
            session['title'] = None if _title_val is None or str(_title_val).strip() == "" else html_encode_but_preserve_quotes(_title_val)

            # Presenter
            _presenter_val = row.get('Name2')
            _presenter_val = fix_common_mojibake(str(_presenter_val)) if pd.notna(_presenter_val) else None
            session['presenter'] = None if _presenter_val is None or str(_presenter_val).strip() == "" else html_encode_but_preserve_quotes(_presenter_val)

            # Email
            _email_val = row.get('E-mail address')
            session['email'] = None if pd.isna(_email_val) or str(_email_val).strip() == "" else str(_email_val).strip()

            # Organization
            _org_val = row.get('School or Organization')
            _org_val = fix_common_mojibake(str(_org_val)) if pd.notna(_org_val) else None
            session['organization'] = None if _org_val is None or str(_org_val).strip() == "" else html_encode_but_preserve_quotes(str(_org_val).strip())
            
            # Description
            _desc_val = row.get('Session Description')
            _desc_val = fix_common_mojibake(str(_desc_val)) if pd.notna(_desc_val) else None
            session['description'] = None if _desc_val is None or str(_desc_val).strip() == "" else html_encode_but_preserve_quotes(_desc_val)
            
            # Add preview field (based on the potentially None description)
            # get_preview should operate on the fixed and HTML-encoded description if it also does HTML stripping
            # However, get_preview strips HTML, so pass the fixed, raw description.
            session['preview'] = get_preview(session['description']) # Pass the already processed description which had mojibake fixed
            
            # MODIFICATION: Populate occurrences array
            if session_id in session_schedule:
                session['occurrences'] = session_schedule[session_id]
            # If session_id is not in session_schedule, 'occurrences' remains an empty list.
            
            sessions_json.append(session)
            # The previous logic for creating multiple entries for multi-occurrence sessions is removed.
            
        # Then, add special events (structure remains unchanged for special events)
        for event in special_events:
            session = {
                'id': f"special_{len(sessions_json) + 1}_{event['title'].replace(' ','_')[:20]}", # Generate a more unique ID
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
                'timeBlock': event['timeBlock'], # Direct timeBlock for special events
                'location': event['location'],   # Direct location for special events
                'tags': ['Special Event'],
                'isSpecialEvent': True
                # No 'occurrences' field for special events by default, they are single events
            }
            sessions_json.append(session)
        
        # MODIFICATION: Update check for unscheduled sessions
        unscheduled_sessions_ids = [s['id'] for s in sessions_json 
                                   if not s.get('isSpecialEvent') and (not s.get('occurrences') or len(s['occurrences']) == 0)]
        if unscheduled_sessions_ids:
            print(f"Warning: {len(unscheduled_sessions_ids)} regular sessions (Strands 1 & 2) are unscheduled or have no occurrence data:")
            for sid in unscheduled_sessions_ids[:5]:
                session_details = next((s for s in sessions_json if s['id'] == sid), None)
                if session_details:
                    print(f"  ID: {sid}, Title: {session_details['title']}")
            if len(unscheduled_sessions_ids) > 5:
                print(f"  ... and {len(unscheduled_sessions_ids) - 5} more")
        
        # MODIFICATION: Update check for sessions in schedule but not in CSV (or filtered out)
        all_csv_session_ids = set(int(r['sessionID']) for _, r in sessions_csv.iterrows() 
                                  if pd.notna(r.get('sessionID')) and str(r.get('sessionID')).isdigit())
        
        # REVERT valid_strand_session_ids TO ORIGINAL LOGIC
        valid_strand_session_ids = set()
        for _, r_csv in sessions_csv.iterrows(): # Use r_csv to avoid conflict with outer 'row'
            if pd.notna(r_csv.get('sessionID')) and str(r_csv.get('sessionID')).isdigit():
                s_text = r_csv.get('Which strand will your presentation be in?', '') # s_text for strand_text
                s_number = '0' # s_number for strand_number
                if isinstance(s_text, str) and 'Strand' in s_text:
                    m = re.search(r'Strand\s+(\d+)', s_text) # Changed to raw string
                    if m:
                        s_number = m.group(1)
                if s_number in ['1', '2']:
                    valid_strand_session_ids.add(int(r_csv['sessionID']))

        scheduled_ids_from_excel = set(session_schedule.keys())
        unknown_schedule_ids = scheduled_ids_from_excel - valid_strand_session_ids
        
        if unknown_schedule_ids:
            print(f"Warning: {len(unknown_schedule_ids)} schedule entries have IDs not in the processed sessions CSV (e.g., wrong strand or missing from CSV):")
            for sid in list(unknown_schedule_ids)[:5]:
                occurrences_info = session_schedule.get(sid)
                if occurrences_info:
                    first_occurrence = occurrences_info[0]
                    print(f"  ID: {sid}, First Occurrence: Location: {first_occurrence['location']}, Time: {first_occurrence['timeBlock']}")
                else:
                    print(f"  ID: {sid} (no occurrence details found, though ID was in schedule_excel keys)")
            if len(unknown_schedule_ids) > 5:
                print(f"  ... and {len(unknown_schedule_ids) - 5} more")
        
        # Write the output JSON
        with open('sessions.json', 'w', encoding='utf-8') as f:
            json.dump(sessions_json, f, ensure_ascii=False, indent=2)
            
        print(f"\\nSuccessfully wrote {len(sessions_json)} entries to sessions.json")
        
        # MODIFICATION: Update summary statistics
        regular_sessions_count = sum(1 for s in sessions_json if not s.get('isSpecialEvent', False))
        special_events_count = sum(1 for s in sessions_json if s.get('isSpecialEvent', False))
        
        # Scheduled regular sessions have non-empty occurrences. Special events have timeBlock.
        scheduled_regular_with_occurrences = sum(1 for s in sessions_json if 
                                                 not s.get('isSpecialEvent', False) and s.get('occurrences') and len(s['occurrences']) > 0)
        scheduled_special_events = sum(1 for s in sessions_json if 
                                       s.get('isSpecialEvent', False) and s.get('timeBlock') and s.get('location'))
        total_scheduled_entries = scheduled_regular_with_occurrences + scheduled_special_events
        
        unscheduled_regular_count = sum(1 for s in sessions_json if 
                                        not s.get('isSpecialEvent', False) and (not s.get('occurrences') or len(s['occurrences']) == 0))

        print(f"\\nSummary:")
        print(f"- Regular session entries (Strands 1 & 2 only): {regular_sessions_count}")
        print(f"- Special event entries: {special_events_count}")
        print(f"- Scheduled regular sessions (with occurrences): {scheduled_regular_with_occurrences}")
        print(f"- Scheduled special events (with time/location): {scheduled_special_events}")
        print(f"- Total scheduled entries in JSON: {total_scheduled_entries}")
        print(f"- Unscheduled regular sessions (Strands 1 & 2 without occurrences): {unscheduled_regular_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
