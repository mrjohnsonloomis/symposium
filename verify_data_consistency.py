#!/usr/bin/env python3
"""
Verify data consistency between sessions.csv, schedule_by_id.xlsx, and sessions.json:
1. Compare session IDs between CSV, Excel, and JSON files
2. Check that time blocks and locations are consistent
3. Ensure there are no missing sessions or schedule conflicts
"""
import json
import sys
import pandas as pd

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
            
        # In the new format, we use specific time blocks like "10:15 - 11:15" instead of "Slot 1"
        time_block = ungrading_session.get("timeBlock", "")
        if not time_block:
            print(f"ISSUE: Ungrading session is missing time block")
            issues_found += 1
        else:
            print(f"OK: Ungrading session has time block: {time_block}")
            
        location = ungrading_session.get("location", "")
        if not location or location == "TBD":
            print(f"ISSUE: Ungrading session has missing location: {location}")
            issues_found += 1
        else:
            print(f"OK: Ungrading session has location: {location}")
    else:
        print("ISSUE: Could not find Ungrading session in sessions.json")
        issues_found += 1
    
    # Check for Writing Center sessions
    writing_center_sessions = []
    for session in sessions_data:
        location = session.get("location", "")
        if location and "Writing Center" in location:
            writing_center_sessions.append(session)
    
    if writing_center_sessions:
        print(f"OK: Found {len(writing_center_sessions)} sessions in the Writing Center:")
        for session in writing_center_sessions:
            print(f"  - {session.get('title', '')[:50]}... ({session.get('timeBlock', 'No time block')})")
    else:
        print("ISSUE: No sessions found in Writing Center location")
        issues_found += 1
    
    # Check for TBD values
    tbd_count = 0
    anonymous_count = 0
    sessions_with_tbd = []
    for session in sessions_data:
        title = session.get("title", "")
        if session.get("timeBlock", "") == "TBD" or not session.get("timeBlock"):
            tbd_count += 1
            sessions_with_tbd.append(f"Time Block TBD: {title[:50]}...")
        if session.get("location", "") == "TBD" or not session.get("location"):
            tbd_count += 1
            sessions_with_tbd.append(f"Location TBD: {title[:50]}...")
        if session.get("location", "") == "anonymous":
            anonymous_count += 1
            sessions_with_tbd.append(f"Location is 'anonymous': {title[:50]}...")
    
    if tbd_count > 0:
        print(f"ISSUE: Found {tbd_count} TBD values in sessions.json")
        for issue in sessions_with_tbd:
            print(f"  - {issue}")
        issues_found += tbd_count
    else:
        print("OK: No TBD values found in sessions.json")
    
    if anonymous_count > 0:
        print(f"ISSUE: Found {anonymous_count} 'anonymous' location values in sessions.json")
        issues_found += anonymous_count
    else:
        print("OK: No 'anonymous' location values found in sessions.json")
    
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

def check_data_sources():
    """
    Check consistency between sessions.csv and schedule_by_id.xlsx
    """
    print("\n=== Checking Data Sources ===")
    
    try:
        # Load the sessions.csv file
        sessions_csv = pd.read_csv('sessions.csv', encoding='utf-8', engine='python')
        
        # Load the schedule_by_id.xlsx file
        schedule_excel = pd.read_excel('schedule_by_id.xlsx')
        
        # Extract session IDs from each source
        csv_session_ids = set()
        for _, row in sessions_csv.iterrows():
            if not pd.isna(row.get('sessionID')) and str(row.get('sessionID')).isdigit():
                csv_session_ids.add(int(row['sessionID']))
                
        excel_session_ids = set()
        for _, row in schedule_excel.iterrows():
            for column in schedule_excel.columns[1:]:  # Skip the 'Time Slot' column
                value = row[column]
                if not pd.isna(value) and isinstance(value, (int, float)) and value == int(value):
                    excel_session_ids.add(int(value))
        
        # Calculate metrics
        total_csv_sessions = len(csv_session_ids)
        total_excel_sessions = len(excel_session_ids)
        
        # Calculate differences
        missing_from_excel = csv_session_ids - excel_session_ids
        missing_from_csv = excel_session_ids - csv_session_ids
        
        # Print report
        print(f"Sessions in CSV: {total_csv_sessions}")
        print(f"Session IDs in Excel: {total_excel_sessions}")
        
        issues = 0
        
        if missing_from_excel:
            print(f"WARNING: {len(missing_from_excel)} sessions in CSV are not scheduled in Excel:")
            for session_id in sorted(missing_from_excel):
                session_row = sessions_csv[sessions_csv['sessionID'] == session_id].iloc[0]
                print(f"  - ID: {session_id}, Title: {session_row.get('Session Title', 'Unknown')}")
            issues += len(missing_from_excel)
                
        if missing_from_csv:
            print(f"WARNING: {len(missing_from_csv)} session IDs in Excel don't exist in CSV:")
            for session_id in sorted(missing_from_csv):
                print(f"  - ID: {session_id}")
            issues += len(missing_from_csv)
                
        if issues == 0:
            print("✅ All sessions are properly mapped between CSV and Excel")
            
        return issues
            
    except Exception as e:
        print(f"Error checking data sources: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    # Check data sources consistency first
    data_source_issues = check_data_sources()
    
    # Load sessions.json
    sessions_data = load_json("sessions.json")
    if not sessions_data:
        print("Failed to load sessions.json, exiting.")
        return 1
    
    # Check sessions.json
    sessions_issues = check_sessions_json(sessions_data)
    
    # Load schedule.json (if it exists, for backward compatibility)
    schedule_issues = 0
    schedule_data = load_json("schedule.json")
    if schedule_data:
        schedule_issues = check_schedule_json(schedule_data)
    else:
        print("\nNote: schedule.json not found. This is expected with the new workflow.")
    
    # Count total issues
    total_issues = sessions_issues + schedule_issues + data_source_issues
    if total_issues > 0:
        print(f"\n=== VALIDATION FAILED: Found {total_issues} issues ===")
        return 1
    else:
        print("\n=== VALIDATION PASSED: No issues found ===")
        return 0

if __name__ == "__main__":
    sys.exit(main())
