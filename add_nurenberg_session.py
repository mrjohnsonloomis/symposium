#!/usr/bin/env python3
"""
Script to add the missing David Nurenberg session to schedule.json
"""
import json
import sys

def add_session_to_schedule():
    try:
        # Load the schedule.json file
        with open('schedule.json', 'r', encoding='utf-8') as f:
            schedule = json.load(f)
        
        # Define the new session for David Nurenberg
        new_session = {
            "timeSlot": "Slot 2 (11:30-12:30)",
            "room": "Brush 203",
            "sessionId": "",
            "title": "Dangerous (Artificial) Minds: Engaging student critical thinking and analysis in their interactions with AI",
            "presenter": "David Nurenberg - Milton Academy",
            "description": "The problem: AI has rendered the traditional English essay, if not obsolete, at least highly problematic from an assessment perspective. How can we be sure we are accurately assessing student knowledge and skills if they are outsourcing their thinking to LLMs? How can we convince students that there is value in learning the knowledge and skills if LLMs can instantly create the same products we are asking them to struggle to develop?",
            "strand": "strand1",
            "strandName": "1: AI in the Classroom",
            "type": "type-presentation",
            "typeName": "Presentation and Q&A",
            "tags": [
                "Humanities",
                "Curriculum Design"
            ]
        }
        
        # Find the correct position to insert the new session
        # We'll insert it after the Brush 202 session for Slot 2
        inserted = False
        for i, session in enumerate(schedule['sessions']):
            if (session['timeSlot'] == "Slot 2 (11:30-12:30)" and 
                session['room'] == "Brush 202"):
                # Insert the new session after this one
                schedule['sessions'].insert(i + 1, new_session)
                inserted = True
                print(f"Added David Nurenberg's session to schedule.json after Brush 202 session")
                break
        
        if not inserted:
            # If we couldn't find a good position, just append it
            schedule['sessions'].append(new_session)
            print(f"Added David Nurenberg's session to schedule.json at the end")
        
        # Save the updated schedule.json
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)
        
        print("Successfully updated schedule.json")
        return True
    
    except Exception as e:
        print(f"Error updating schedule.json: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting to add David Nurenberg's session to schedule.json...")
    success = add_session_to_schedule()
    if success:
        print("Successfully added David Nurenberg's session to schedule.json")
    else:
        print("Failed to add David Nurenberg's session to schedule.json")
        sys.exit(1)
