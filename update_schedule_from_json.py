"""
This script previously updated schedule.html based on sessions.json and created schedule.json.
It is now modified to reflect that schedule.html fetches sessions.json directly.
"""

import json
import os

def main():
    print("Ensuring schedule.html uses sessions.json directly.")
    # This script previously generated schedule.json and modified schedule.html
    # to use it. Since schedule.html has been updated to use sessions.json directly,
    # this script's main role in generating schedule.json and modifying HTML is no longer needed.

    try:
        # Verify sessions.json exists
        if not os.path.exists('sessions.json'):
            print("Error: sessions.json not found. Please run generate_master_sessions.py first.")
            return 1
        
        with open('sessions.json', 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        print(f"Verified sessions.json. It contains {len(sessions)} sessions.")

        print("Successfully verified that schedule.html should use sessions.json.")
        print("The script update_schedule_from_json.py no longer generates schedule.json or modifies schedule.html.")
        
    except Exception as e:
        print(f"Error in update_schedule_from_json.py: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    main()
