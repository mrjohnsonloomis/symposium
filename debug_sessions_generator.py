"""
Simplified script to debug the master sessions generator
"""

import pandas as pd
import json
import sys

def main():
    print("Starting simplified debug script...")
    
    try:
        # Step 1: Read the files
        print("Reading sessions.csv...")
        sessions_csv = pd.read_csv('sessions.csv', encoding='utf-8')
        print(f"Successfully read {len(sessions_csv)} sessions")
        
        print("\nReading schedule_by_id.xlsx...")
        schedule_excel = pd.read_excel('schedule_by_id.xlsx')
        print(f"Successfully read {len(schedule_excel)} rows from schedule Excel")
        
        # Step 2: Process session IDs from Excel
        print("\nProcessing Excel schedule...")
        session_schedule = {}
        for index, row in schedule_excel.iterrows():
            time_slot = row['Time Slot']
            if pd.isna(time_slot):
                continue
                
            print(f"Row {index}: Time Slot = {time_slot}")
            
            # Process only first 3 columns as a test
            test_columns = schedule_excel.columns[:3]
            for room in test_columns[1:]:
                session_id = row[room]
                if pd.isna(session_id):
                    continue
                
                try:
                    # Convert to integer if it's a number
                    session_id = int(session_id)
                    print(f"  Found session ID {session_id} in {room}")
                    session_schedule[session_id] = {
                        'location': room,
                        'timeBlock': time_slot
                    }
                except (ValueError, TypeError) as e:
                    print(f"  Error converting '{session_id}' in {room} to integer: {e}")
        
        print(f"\nExtracted {len(session_schedule)} session schedule entries")
        
        # Step 3: Process a single session from CSV as a test
        print("\nProcessing first few sessions from CSV...")
        test_sessions = []
        for index, row in sessions_csv.head(3).iterrows():
            # Debug the session ID extraction
            session_id_raw = row.get('sessionID', 'MISSING')
            print(f"Row {index}: Session ID = {session_id_raw} (type: {type(session_id_raw)})")
            
            if pd.isna(session_id_raw) or not str(session_id_raw).isdigit():
                print(f"  Skipping row {index}: Invalid session ID")
                continue
                
            session_id = int(session_id_raw)
            
            # Create a minimal test session object
            session = {
                'id': session_id,
                'title': row.get('Session Title', ''),
                'presenter': row.get('Name2', ''),
            }
            
            # Add location and time if available
            if session_id in session_schedule:
                session['timeBlock'] = session_schedule[session_id]['timeBlock']
                session['location'] = session_schedule[session_id]['location']
                print(f"  Added schedule info: {session_schedule[session_id]}")
            else:
                session['timeBlock'] = ''
                session['location'] = ''
                print(f"  No schedule info found for session ID {session_id}")
            
            test_sessions.append(session)
        
        print(f"\nCreated {len(test_sessions)} test sessions")
        
        # Write a test output
        print("\nWriting test_sessions.json...")
        with open('test_sessions.json', 'w', encoding='utf-8') as f:
            json.dump(test_sessions, f, ensure_ascii=False, indent=2)
        
        print("Script completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
