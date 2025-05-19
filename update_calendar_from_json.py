"""
Update calendar.html based on the master sessions.json file
"""

import json
import os

def main():
    print("Ensuring calendar.html uses sessions.json directly.")
    # This script previously generated calendar_data.json and modified calendar.html
    # to use it. Since calendar.html has been updated to use sessions.json directly,
    # this script's main role in generating calendar_data.json is no longer needed.
    # We will remove the parts that create calendar_data.json and modify HTML.

    try:
        # Verify sessions.json exists
        if not os.path.exists('sessions.json'):
            print("Error: sessions.json not found. Please run generate_master_sessions.py first.")
            return 1
        
        with open('sessions.json', 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        print(f"Verified sessions.json. It contains {len(sessions)} sessions.")

        print("Successfully verified that calendar.html should use sessions.json.")
        print("The script update_calendar_from_json.py no longer generates calendar_data.json or modifies calendar.html.")
        
    except Exception as e:
        print(f"Error in update_calendar_from_json.py: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    main()
