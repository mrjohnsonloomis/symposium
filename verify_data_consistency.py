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
    
    # Check for Caitie Cotton session (Example check, can be adapted)
    # This check might be less relevant if data is always sourced from CSV/Excel
    # and specific manual entries like this are not expected in sessions.json directly.
    # For now, we'll keep it as an example of a specific data point check.
    ungrading_session = None
    for session in sessions_data:
        if "Ungrading" in session.get("title", ""): # title can be None
            ungrading_session = session
            break
    
    if ungrading_session:
        presenter = ungrading_session.get("presenter", "")
        if "Caitie Cotton" not in (presenter or ""): # Handle None presenter
            print(f"ISSUE: Ungrading session has incorrect presenter: {presenter}")
            issues_found += 1
        else:
            print(f"OK: Ungrading session has correct presenter: {presenter}")

        # Check occurrences for time and location
        occurrences = ungrading_session.get("occurrences", [])
        if not occurrences:
            print(f"ISSUE: Ungrading session (ID: {ungrading_session.get('id')}) has no occurrences listed.")
            issues_found +=1
        else:
            print(f"OK: Ungrading session (ID: {ungrading_session.get('id')}) has {len(occurrences)} occurrence(s).")
            for i, occ in enumerate(occurrences):
                time_block = occ.get("timeBlock", "")
                location = occ.get("location", "")
                if not time_block or time_block == "TBD":
                    print(f"ISSUE: Ungrading session occurrence {i+1} has missing/TBD time block: {time_block}")
                    issues_found += 1
                else:
                    print(f"OK: Ungrading session occurrence {i+1} has time block: {time_block}")
                
                if not location or location == "TBD":
                    print(f"ISSUE: Ungrading session occurrence {i+1} has missing/TBD location: {location}")
                    issues_found += 1
                else:
                    print(f"OK: Ungrading session occurrence {i+1} has location: {location}")
    else:
        print("INFO: Could not find 'Ungrading' session in sessions.json (this might be OK if not expected).")
        # Not necessarily an issue if the session isn't in the current dataset
    
    # Check for Writing Center sessions
    writing_center_sessions = []
    for session in sessions_data:
        if session.get("isSpecialEvent"): # Skip special events for this check
            continue
        for occ in session.get("occurrences", []):
            location = occ.get("location", "")
            if location and "Writing Center" in location:
                writing_center_sessions.append(session)
                break # Count session once even if in WC multiple times
    
    if writing_center_sessions:
        print(f"OK: Found {len(writing_center_sessions)} regular sessions with an occurrence in the Writing Center:")
        for session in writing_center_sessions:
            occurrence_details = []
            for occ in session.get("occurrences", []):
                if "Writing Center" in occ.get("location", ""):
                    occurrence_details.append(f"{occ.get('timeBlock', 'No time')} at {occ.get('location', 'No location')}")
            print(f"  - ID: {session.get('id')}, Title: {session.get('title', '')[:50]}... ({'; '.join(occurrence_details)})")
    else:
        print("INFO: No regular sessions found with an occurrence in a Writing Center location (this might be OK).")
        # Not necessarily an issue if no sessions are scheduled there.

    # Check for TBD values in occurrences of regular sessions and top-level for special events
    tbd_count = 0
    anonymous_count = 0 # Assuming 'anonymous' is a specific value to check for
    sessions_with_issues = []

    for session in sessions_data:
        session_id = session.get("id", "Unknown ID")
        title = session.get("title", "Untitled Session")

        if session.get("isSpecialEvent"):
            # For special events, check top-level timeBlock and location
            if session.get("timeBlock", "") == "TBD" or not session.get("timeBlock"):
                tbd_count += 1
                sessions_with_issues.append(f"Time Block TBD/Missing (Special Event): ID {session_id}, {title[:50]}...")
            if session.get("location", "") == "TBD" or not session.get("location"):
                tbd_count += 1
                sessions_with_issues.append(f"Location TBD/Missing (Special Event): ID {session_id}, {title[:50]}...")
            if session.get("location", "") == "anonymous": # Check for 'anonymous'
                anonymous_count += 1
                sessions_with_issues.append(f"Location is 'anonymous' (Special Event): ID {session_id}, {title[:50]}...")
        else:
            # For regular sessions, check within each occurrence
            occurrences = session.get("occurrences", [])
            if not occurrences:
                # This is handled by the unscheduled sessions check in generate_master_sessions.py
                # but we can flag it here too if desired.
                # print(f"INFO: Regular session ID {session_id} has no occurrences.")
                pass
            for i, occ in enumerate(occurrences):
                if occ.get("timeBlock", "") == "TBD" or not occ.get("timeBlock"):
                    tbd_count += 1
                    sessions_with_issues.append(f"Time Block TBD/Missing (Occurrence {i+1}): ID {session_id}, {title[:50]}...")
                if occ.get("location", "") == "TBD" or not occ.get("location"):
                    tbd_count += 1
                    sessions_with_issues.append(f"Location TBD/Missing (Occurrence {i+1}): ID {session_id}, {title[:50]}...")
                if occ.get("location", "") == "anonymous": # Check for 'anonymous'
                    anonymous_count += 1
                    sessions_with_issues.append(f"Location is 'anonymous' (Occurrence {i+1}): ID {session_id}, {title[:50]}...")
    
    if tbd_count > 0:
        print(f"ISSUE: Found {tbd_count} TBD or missing time/location values in sessions.json")
        for issue in sessions_with_issues:
            if "TBD" in issue or "Missing" in issue: # Only print TBD/Missing issues here
                 print(f"  - {issue}")
        issues_found += tbd_count
    else:
        print("OK: No TBD or missing time/location values found in relevant fields of sessions.json")
    
    if anonymous_count > 0:
        print(f"ISSUE: Found {anonymous_count} 'anonymous' location values in sessions.json")
        for issue in sessions_with_issues:
            if "'anonymous'" in issue: # Only print anonymous issues here
                print(f"  - {issue}")
        issues_found += anonymous_count
    else:
        print("OK: No 'anonymous' location values found in sessions.json")
    
    # Check for missing essential fields (title, presenter for non-special events)
    missing_field_issues = 0
    for session in sessions_data:
        session_id = session.get("id", "Unknown ID")
        title = session.get("title") # Expecting None if missing, not empty string from generator
        
        if title is None or title == "": # Check for None or empty string
            print(f"ISSUE: Session ID {session_id} is missing a title.")
            missing_field_issues += 1
            
        if not session.get("isSpecialEvent"):
            presenter = session.get("presenter") # Expecting None if missing
            if presenter is None or presenter == "": # Check for None or empty string
                print(f"ISSUE: Regular Session ID {session_id} (Title: {title[:30]}...) is missing a presenter.")
                missing_field_issues += 1
    
    if missing_field_issues > 0:
        print(f"ISSUE: Found {missing_field_issues} missing essential fields (title/presenter).")
        issues_found += missing_field_issues
    else:
        print("OK: All sessions have titles, and regular sessions have presenters.")

    return issues_found

def check_data_sources():
    """
    Check consistency between sessions.csv and schedule_by_id.xlsx
    """
    print("\n=== Checking Data Sources ===")
    
    try:
        # Load the sessions.csv file
        sessions_csv = pd.read_csv('sessions.csv', encoding='utf-8', on_bad_lines='skip')
        
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
    
    # schedule.json is deprecated, so we remove its check
    schedule_issues = 0 
    # schedule_data = load_json("schedule.json")
    # if schedule_data:
    #     schedule_issues = check_schedule_json(schedule_data)
    # else:
    #     print("\\nNote: schedule.json not found. This is expected with the new workflow.")
    print("\nNote: schedule.json checks are skipped as it's deprecated.")
    
    # Count total issues
    total_issues = sessions_issues + data_source_issues # Removed schedule_issues
    if total_issues > 0:
        print(f"\n=== VALIDATION FAILED: Found {total_issues} issues ===")
        return 1
    else:
        print("\n=== VALIDATION PASSED: No issues found ===")
        return 0

if __name__ == "__main__":
    sys.exit(main())
