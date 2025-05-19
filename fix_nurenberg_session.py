#!/usr/bin/env python3
"""
Fix the David Nurenberg session in sessions.json and schedule.json
to ensure proper consistency between the two files.
"""
import json
import sys

def fix_nurenberg_session():
    print("Starting to fix David Nurenberg's session...")
    
    try:
        # Load sessions.json and fix any formatting issues
        with open('sessions.json', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if there's a format issue with David Nurenberg's session
        if '"title": "Dangerous (Artificial) Minds:' in content and '"strand":' not in content[:content.find('"title": "Dangerous (Artificial) Minds:')]:
            # Manually fix the JSON formatting
            print("Detected formatting issue in sessions.json. Fixing it...")
            # Find the position where David Nurenberg's session starts
            start_pos = content.find('"title": "Dangerous (Artificial) Minds:')
            if start_pos != -1:
                # Find the position of the preceding session's closing brace
                end_of_prev = content.rfind("}", 0, start_pos)
                if end_of_prev != -1:
                    # Insert the missing fields after the closing brace of the previous session
                    fixed_content = content[:end_of_prev+1] + ',\n  {\n    "strand": "strand1",\n    "strandName": "1: AI in the Classroom",\n    "type": "type-presentation",\n    "typeName": "Presentation and Q&A",\n    ' + content[start_pos:]
                    
                    # Write the fixed content back to the file
                    with open('sessions.json', 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    print("Fixed JSON formatting in sessions.json")
        
        # Now load the fixed JSON files
        with open('sessions.json', 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        # Load schedule.json
        with open('schedule.json', 'r', encoding='utf-8') as f:
            schedule = json.load(f)
            
        # Find David Nurenberg's session in sessions.json and fix it
        nurenberg_session_found = False
        fixed_nurenberg_session = None
        
        for i, session in enumerate(sessions):
            presenter = session.get('presenter', '')
            title = session.get('title', '')
            if 'David Nurenberg' in presenter or ('Dangerous' in title and 'Mind' in title):
                nurenberg_session_found = True
                print(f"Found David Nurenberg's session at index {i}")
                
                # Ensure all fields are present
                if 'strand' not in session:
                    session['strand'] = 'strand1'
                    print("Added missing 'strand' field")
                
                if 'strandName' not in session:
                    session['strandName'] = "1: AI in the Classroom"
                    print("Added missing 'strandName' field")
                
                if 'type' not in session:
                    session['type'] = 'type-presentation'
                    print("Added missing 'type' field")
                
                if 'typeName' not in session:
                    session['typeName'] = "Presentation and Q&A"
                    print("Added missing 'typeName' field")
                
                if 'title' not in session:
                    session['title'] = "Dangerous (Artificial) Minds: Engaging student critical thinking and analysis in their interactions with AI"
                    print("Added missing 'title' field")
                
                # Update time block and location from schedule
                session['timeBlock'] = "Slot 2 (11:30-12:30)"
                session['location'] = "Brush 203"
                print("Updated timeBlock and location")
                
                fixed_nurenberg_session = session
                break
                
        if not nurenberg_session_found:
            print("Could not find David Nurenberg's session in sessions.json")
            return False
        
        # Find or add David Nurenberg's session in schedule.json
        nurenberg_schedule_found = False
        
        for session in schedule.get('sessions', []):
            if 'David Nurenberg' in session.get('presenter', ''):
                nurenberg_schedule_found = True
                print("Found David Nurenberg's session in schedule.json")
                break
        
        if not nurenberg_schedule_found:
            # Add it to schedule.json based on our fixed session
            new_schedule_session = {
                "timeSlot": fixed_nurenberg_session['timeBlock'],
                "room": fixed_nurenberg_session['location'],
                "sessionId": "",
                "title": fixed_nurenberg_session['title'],
                "presenter": fixed_nurenberg_session['presenter'],
                "description": fixed_nurenberg_session['description'],
                "strand": fixed_nurenberg_session['strand'],
                "strandName": fixed_nurenberg_session['strandName'],
                "type": fixed_nurenberg_session['type'],
                "typeName": fixed_nurenberg_session['typeName'],
                "tags": fixed_nurenberg_session['tags']
            }
            
            # Find where to insert - after Brush 202 session for Slot 2
            inserted = False
            for i, session in enumerate(schedule['sessions']):
                if (session['timeSlot'] == "Slot 2 (11:30-12:30)" and 
                    session['room'] == "Brush 202"):
                    # Insert the new session after this one
                    schedule['sessions'].insert(i + 1, new_schedule_session)
                    inserted = True
                    print(f"Added David Nurenberg's session to schedule.json after Brush 202 session")
                    break
            
            if not inserted:
                # If we couldn't find a good position, just append it
                schedule['sessions'].append(new_schedule_session)
                print(f"Added David Nurenberg's session to schedule.json at the end")
        
        # Save the updated files
        with open('sessions.json', 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
        
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)
        
        print("Successfully updated both files")
        return True
    
    except Exception as e:
        print(f"Error fixing David Nurenberg's session: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting to fix David Nurenberg's session in sessions.json and schedule.json...")
    success = fix_nurenberg_session()
    if success:
        print("Successfully fixed David Nurenberg's session in both files")
    else:
        print("Failed to fix David Nurenberg's session")
        sys.exit(1)
