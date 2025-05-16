#!/usr/bin/env python3
"""
Fix missing or incorrect time blocks and locations in sessions.json
"""
import json
import os

# Dictionary mapping presenter names to their correct room and time slot
SESSION_UPDATES = {
    "Annie Murphy Paul": {
        "timeBlock": "Slot 1 (10:15-11:15)",
        "location": "Room A"
    },
    "Scott MacClintic": {
        "timeBlock": "Slot 3 (1:30-2:30)",
        "location": "Writing Center"
    },
    "Jen Solomon": {
        "timeBlock": "Slot 1 (10:15-11:15)",
        "location": "Brush 308"
    },
    "David Nurenberg": {
        "timeBlock": "Slot 2 (11:30-12:30)",
        "location": "Brush 203"
    },
    "Meghan Chew": {
        "timeBlock": "Slot 3 (1:30-2:30)",
        "location": "Brush 203"
    },
    "Adam Alsamadisi": {
        "timeBlock": "Slot 1 (10:15-11:15)",
        "location": "Brush 306"
    },
    "Kyle Conrau-Lewis": {
        "timeBlock": "Slot 1 (10:15-11:15)",
        "location": "Writing Center"
    }
}

def fix_sessions():
    # Load sessions from file
    with open('sessions.json', 'r', encoding='utf-8') as file:
        sessions = json.load(file)
    
    updates_made = 0
    
    # Process each session
    for session in sessions:
        presenter = session.get("presenter", "")
        # Extract the presenter name without the school/affiliation
        presenter_name = presenter.split(" - ")[0] if " - " in presenter else presenter
        
        # Try to match the presenter name to our updates dictionary
        for name, updates in SESSION_UPDATES.items():
            if name in presenter_name:
                # Fix email field if it contains a date
                if session.get("email") and not "@" in session["email"]:
                    session["email"] = "anonymous"  # Reset to anonymous
                
                # Update timeBlock if needed
                if session.get("timeBlock") == "TBD" or not session.get("timeBlock"):
                    session["timeBlock"] = updates["timeBlock"]
                    print(f"Updated timeBlock for {presenter_name}: {updates['timeBlock']}")
                
                # Update location if needed
                if session.get("location") == "anonymous" or not session.get("location"):
                    session["location"] = updates["location"]
                    print(f"Updated location for {presenter_name}: {updates['location']}")
                
                updates_made += 1
                break
    
    # Save the updated sessions back to the file
    with open('sessions.json', 'w', encoding='utf-8') as file:
        json.dump(sessions, file, indent=2, ensure_ascii=False)
    
    print(f"\nCompleted session fixes: {updates_made} sessions updated.")

if __name__ == "__main__":
    fix_sessions()
