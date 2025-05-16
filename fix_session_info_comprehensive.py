#!/usr/bin/env python3
"""
Comprehensive fix for session information issues:
1. Fix missing or incorrect time blocks and locations in sessions.json based on schedule_temp.csv
2. Fix presenter names using emails as the authoritative source
3. Sync sessions.json and schedule.json for consistency
"""
import json
import csv
import os
import re

def clean_title(title):
    """Remove any presenter prefix and normalize quotes"""
    # Remove prefix like "Cotton: "
    clean = re.sub(r'^[A-Za-z]+:\s*', '', title)
    # Normalize quotes
    clean = clean.replace('"', '"').replace('"', '"')
    return clean.strip()

def load_csv_sessions():
    """Load sessions from CSV file to get email/presenter mapping"""
    email_presenter_map = {}
    try:
        with open('sessions.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header
            
            # Manual column mapping based on the CSV structure
            presenter_idx = 6  # "Name2" column
            email_idx = 7      # "E-mail address" column
            
            print(f"Using columns: Presenter ({header[presenter_idx]}), Email ({header[email_idx]})")
            
            if presenter_idx is None or email_idx is None:
                print("Could not find presenter or email columns in CSV")
                return {}
                
            for row in reader:
                if len(row) > max(presenter_idx, email_idx):
                    email = row[email_idx].strip()
                    presenter = row[presenter_idx].strip()
                    
                    # Extract presenter name from email if available
                    if email and "@" in email and presenter:
                        email_presenter_map[email] = presenter
        
        return email_presenter_map
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return {}

def load_schedule_assignments():
    """Load room and time assignments from schedule_temp.csv"""
    session_assignments = {}
    
    try:
        with open('schedule_temp.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Get room names from header
            
            # Skip headers for arrival, keynote
            time_slots = []
            for row in reader:
                if not row or not row[0]:  # Skip empty rows
                    continue
                
                time_slot = row[0].strip()
                time_slots.append(time_slot)
                
                # Skip non-session time slots like arrival, keynote, closing
                if not time_slot.startswith("Slot"):
                    continue
                
                # Process each room's session
                for i in range(1, len(row)):
                    if i >= len(headers) or not row[i]:  # Skip empty cells
                        continue
                    
                    room = headers[i].strip()
                    cell_content = row[i].strip()
                    
                    # Skip empty cells
                    if not cell_content:
                        continue
                    
                    # Extract presenter and title
                    parts = cell_content.split(':', 1)
                    if len(parts) != 2:
                        continue  # Invalid format
                    
                    presenter_last_name = parts[0].strip()
                    title = parts[1].strip()
                    clean_session_title = clean_title(title)
                    
                    # Store by title for easy lookup
                    if clean_session_title not in session_assignments:
                        session_assignments[clean_session_title] = []
                    
                    # Add this occurrence
                    session_assignments[clean_session_title].append({
                        'timeBlock': time_slot,
                        'location': room,
                        'presenter_last_name': presenter_last_name
                    })
        
        return session_assignments, time_slots
    except Exception as e:
        print(f"Error loading schedule CSV: {e}")
        return {}, []

def update_presenter_names(sessions, email_presenter_map):
    """Update presenter names based on email field"""
    presenter_updates = 0
    
    # Special case for Caitie Cotton - hardcoded fix
    for session in sessions:
        title = session.get('title', '')
        if "Ungrading" in title and "Humanities" in title:
            current_presenter = session.get('presenter', '')
            if current_presenter != "Caitie Cotton - Loomis Chaffee":
                session['presenter'] = "Caitie Cotton - Loomis Chaffee"
                presenter_updates += 1
                print(f"Fixed presenter for '{title[:50]}...': '{current_presenter}' → 'Caitie Cotton - Loomis Chaffee'")
    
    # General case using email mapping
    for session in sessions:
        email = session.get('email', '')
        current_presenter = session.get('presenter', '')
        
        # Find correct presenter name from email
        if '@' in email and email in email_presenter_map:
            csv_presenter = email_presenter_map[email]
            if csv_presenter and csv_presenter != current_presenter:
                # Handle other potential email/presenter mismatches
                name_parts = email.split('@')[0].split('.')
                if len(name_parts) >= 2:
                    first_name = name_parts[0].capitalize()
                    last_name = name_parts[1].capitalize()
                    
                    # Extract affiliation if available
                    affiliation = ""
                    if " - " in current_presenter:
                        affiliation = " - " + current_presenter.split(" - ")[1]
                        
                    new_presenter = f"{first_name} {last_name}{affiliation}"
                    session['presenter'] = new_presenter
                    presenter_updates += 1
                    print(f"Updated presenter: '{current_presenter}' → '{new_presenter}'")
    
    return presenter_updates

def update_schedule_info(sessions, schedule_assignments):
    """Update time blocks and locations based on schedule"""
    updates_made = 0
    
    for session in sessions:
        title = session.get('title', '')
        clean_session_title = clean_title(title)
        
        # Try to find matching session in schedule assignments
        assignments = schedule_assignments.get(clean_session_title, [])
        if assignments:
            # Check if session has multiple time slots
            if len(assignments) > 1:
                # Combine time blocks
                time_blocks = [a['timeBlock'] for a in assignments]
                time_blocks_str = " and ".join(time_blocks)
                
                # Use the first location as default
                location = assignments[0]['location']
                
                if session.get('timeBlock', '') != time_blocks_str:
                    print(f"Updated timeBlock for '{title[:50]}...': '{session.get('timeBlock', 'None')}' → '{time_blocks_str}'")
                    session['timeBlock'] = time_blocks_str
                    updates_made += 1
                
                if session.get('location', '') != location:
                    print(f"Updated location for '{title[:50]}...': '{session.get('location', 'None')}' → '{location}'")
                    session['location'] = location
                    updates_made += 1
            else:
                # Single time slot
                assignment = assignments[0]
                
                if (session.get('timeBlock', '') != assignment['timeBlock'] and 
                    session.get('timeBlock', '') != "TBD"):
                    print(f"Updated timeBlock for '{title[:50]}...': '{session.get('timeBlock', 'None')}' → '{assignment['timeBlock']}'")
                    session['timeBlock'] = assignment['timeBlock']
                    updates_made += 1
                
                if (session.get('location', '') != assignment['location'] and 
                    session.get('location', '') != "TBD"):
                    print(f"Updated location for '{title[:50]}...': '{session.get('location', 'None')}' → '{assignment['location']}'")
                    session['location'] = assignment['location']
                    updates_made += 1
    
    return updates_made

def update_schedule_json(sessions_data, schedule_path='schedule.json'):
    """Update presenter information in schedule.json for consistency"""
    try:
        # Create a lookup dictionary for quick access
        session_lookup = {}
        for session in sessions_data:
            title = session.get('title', '')
            if title:
                session_lookup[title] = session
        
        # Load schedule.json
        with open(schedule_path, 'r', encoding='utf-8') as file:
            schedule_data = json.load(file)
        
        schedule_updates = 0
        # Update sessions in schedule.json
        for session in schedule_data.get('sessions', []):
            title = session.get('title', '')
            if title in session_lookup:
                original_session = session_lookup[title]
                if session.get('presenter', '') != original_session.get('presenter', ''):
                    print(f"Updating schedule.json presenter for '{title[:50]}...': '{session.get('presenter', 'None')}' → '{original_session.get('presenter', '')}'")
                    session['presenter'] = original_session.get('presenter', '')
                    schedule_updates += 1
        
        # Write back to schedule.json
        with open(schedule_path, 'w', encoding='utf-8') as file:
            json.dump(schedule_data, file, indent=2, ensure_ascii=False)
        
        print(f"\nUpdated {schedule_updates} presenter entries in schedule.json")
        return schedule_updates
    
    except Exception as e:
        print(f"Error updating schedule.json: {e}")
        return 0

def main():
    print("Starting comprehensive session information fix...")
    
    # Load email-to-presenter mapping from CSV
    email_presenter_map = load_csv_sessions()
    print(f"Loaded {len(email_presenter_map)} email-to-presenter mappings from CSV")
    
    # Load schedule assignments from schedule_temp.csv
    schedule_assignments, time_slots = load_schedule_assignments()
    print(f"Loaded {len(schedule_assignments)} session assignments from schedule CSV")
    print(f"Time slots found: {', '.join(time_slots)}")
    
    try:
        # Load sessions.json
        with open('sessions.json', 'r', encoding='utf-8') as file:
            sessions_data = json.load(file)
        
        print(f"\nProcessing {len(sessions_data)} sessions...")
        
        # Update presenter names
        presenter_updates = update_presenter_names(sessions_data, email_presenter_map)
        print(f"Updated {presenter_updates} presenter names")
        
        # Update schedule info
        schedule_updates = update_schedule_info(sessions_data, schedule_assignments)
        print(f"Updated {schedule_updates} schedule entries (time blocks and locations)")
        
        # Save updated sessions.json
        with open('sessions.json', 'w', encoding='utf-8') as file:
            json.dump(sessions_data, file, indent=2, ensure_ascii=False)
        
        print(f"\nSaved updated sessions.json")
        
        # Update schedule.json
        update_schedule_json(sessions_data)
        
        print("\nCompleted session information fix!")
    
    except Exception as e:
        print(f"Error processing session data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
