#!/usr/bin/env python3
"""
Verify that sessions.json and schedule.json are consistent:
1. Check that Caitie Cotton's session has the correct presenter
2. Check that time blocks and locations are consistent
3. Ensure there are no "TBD" values for time blocks and locations
"""
import json
import sys

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def check_sessions_json(sessions_data):
    issues_found = 0
    print("\n=== Checking sessions.json ===")
    
    # Check for Caitie Cotton session
    ungrading_session = None
    for session in sessions_data:
        if "Ungrading" in session.get("title", ""):
            ungrading_session = session
            break
    
    if ungrading_session:
        presenter = ungrading_session.get("presenter", "")
        if "Caitie Cotton" not in presenter:
            print(f"ISSUE: Ungrading session has incorrect presenter: {presenter}")
            issues_found += 1
        else:
            print(f"OK: Ungrading session has correct presenter: {presenter}")
            
        time_block = ungrading_session.get("timeBlock", "")
        if "Slot 1" not in time_block or "Slot 3" not in time_block:
            print(f"ISSUE: Ungrading session has incorrect time block: {time_block}")
            issues_found += 1
        else:
            print(f"OK: Ungrading session has correct time blocks: {time_block}")
            
        location = ungrading_session.get("location", "")
        if not location or location == "TBD":
            print(f"ISSUE: Ungrading session has missing location: {location}")
            issues_found += 1
        else:
            print(f"OK: Ungrading session has location: {location}")
    else:
        print("ISSUE: Could not find Ungrading session in sessions.json")
        issues_found += 1
    
    # Check for TBD values
    tbd_count = 0
    sessions_with_tbd = []
    for session in sessions_data:
        title = session.get("title", "")
        if session.get("timeBlock", "") == "TBD" or not session.get("timeBlock"):
            tbd_count += 1
            sessions_with_tbd.append(f"Time Block TBD: {title[:50]}...")
        if session.get("location", "") == "TBD" or not session.get("location"):
            tbd_count += 1
            sessions_with_tbd.append(f"Location TBD: {title[:50]}...")
    
    if tbd_count > 0:
        print(f"ISSUE: Found {tbd_count} TBD values in sessions.json")
        for issue in sessions_with_tbd:
            print(f"  - {issue}")
        issues_found += tbd_count
    else:
        print("OK: No TBD values found in sessions.json")
    
    return issues_found

def check_schedule_json(schedule_data):
    issues_found = 0
    print("\n=== Checking schedule.json ===")
    
    # Check for Caitie Cotton sessions
    ungrading_sessions = []
    for session in schedule_data.get("sessions", []):
        if "Ungrading" in session.get("title", ""):
            ungrading_sessions.append(session)
    
    if ungrading_sessions:
        for session in ungrading_sessions:
            presenter = session.get("presenter", "")
            if "Caitie Cotton" not in presenter:
                print(f"ISSUE: Ungrading session has incorrect presenter: {presenter} in time slot {session.get('timeSlot', '')}")
                issues_found += 1
            else:
                print(f"OK: Ungrading session has correct presenter: {presenter} in time slot {session.get('timeSlot', '')}")
    else:
        print("ISSUE: Could not find Ungrading session in schedule.json")
        issues_found += 1
    
    return issues_found

def main():
    # Load sessions.json
    sessions_data = load_json("sessions.json")
    if not sessions_data:
        print("Failed to load sessions.json, exiting.")
        return 1
    
    # Load schedule.json
    schedule_data = load_json("schedule.json")
    if not schedule_data:
        print("Failed to load schedule.json, exiting.")
        return 1
    
    # Check both files
    sessions_issues = check_sessions_json(sessions_data)
    schedule_issues = check_schedule_json(schedule_data)
    
    total_issues = sessions_issues + schedule_issues
    if total_issues > 0:
        print(f"\n=== VALIDATION FAILED: Found {total_issues} issues ===")
        return 1
    else:
        print("\n=== VALIDATION PASSED: No issues found ===")
        return 0

if __name__ == "__main__":
    sys.exit(main())
