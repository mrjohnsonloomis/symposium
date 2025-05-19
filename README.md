# Symposium Website Data Management

This documentation explains how the symposium website's data system works and how to maintain consistency across different views.

## Data Structure Overview

The symposium website uses two main JSON files for displaying session information across different views:

1. **sessions.json**: Used by the Session Listing view (index.html)
   - Contains detailed information about each session
   - Generated primarily from sessions.csv

2. **schedule.json**: Used by the Schedule view (schedule.html) and Calendar view (calendar.html)
   - Contains time slot and room assignments for all sessions
   - Generated primarily from session_schedule_by_slot.xlsx (via schedule_temp.csv)

## Data Flow

The data flow follows this sequence:
1. Raw data is stored in CSV and Excel files 
   - `sessions.csv` - Session details submitted by presenters
   - `session_schedule_by_slot.xlsx` - Room and time assignments

2. Data is processed using Python scripts:
   - `csv_to_json.py` - Converts session details from CSV to JSON
   - `update_schedule.py` - Creates schedule data from Excel
   - `excel_to_schedule.py` - Updates calendar view data
   - `update_rooms.py` - Updates room assignments in all files
   - `update_sessions.py` - Updates session information with schedule details

3. Synchronization scripts ensure consistency:
   - `fix_session_info_comprehensive.py` - Fixes specific session information issues
   - `sync_session_data.py` - Ensures sessions.json and schedule.json are in sync
   - `verify_data_consistency.py` - Checks for inconsistencies in the data

## Common Issues and Solutions

### 1. Inconsistent Presenter Names

**Problem**: A presenter appears with different names in sessions.json vs schedule.json  
**Solution**: Run `sync_session_data.py` to fix inconsistencies

### 2. Missing Time Blocks or Locations

**Problem**: Sessions appear without time blocks or with "TBD" locations  
**Solution**: 
- Check `sessions.csv` for missing data
- Update the SESSION_UPDATES dictionary in `fix_session_info.py`
- Run `update_all.sh` to apply all fixes

### 3. Sessions Appear in Schedule but Not Session Cards

**Problem**: A session appears in schedule.json but not in sessions.json  
**Solution**: 
- Add the session to sessions.json using a script like `add_nurenberg_session.py`
- Run `sync_session_data.py` to ensure consistency

### 4. Special Case: David Nurenberg's Session

**Problem**: David Nurenberg's session has special formatting requirements that need to be maintained  
**Solution**:
- The `fix_nurenberg_session.py` script fixes formatting issues in both files
- This script runs as part of the update_all.sh process (Step 8)

**Problem**: Sessions show up in schedule.html but not in index.html  
**Solution**: Run `sync_session_data.py` to reconcile differences between the data files

### 4. Adding New Sessions

**Problem**: New sessions need to be added to both data files  
**Solution**:
1. Add the session to sessions.csv
2. Update session_schedule_by_slot.xlsx with the room and time assignment
3. Run `update_all.sh` to regenerate all data files

## Maintenance Best Practices

1. **Always Update Source Files First**: Make changes to sessions.csv or session_schedule_by_slot.xlsx, not directly to JSON files
2. **Run the Complete Update Script**: Use `update_all.sh` to process all changes at once
3. **Verify Data Consistency**: Run `verify_data_consistency.py` to check for issues
4. **Special Cases**: For sessions that need custom handling, update the appropriate scripts:
   - For sessions with special room/time needs: Update `fix_session_info.py`
   - For title matching issues: Update the matching logic in `sync_session_data.py`

## Scripts Reference

- **update_all.sh**: Main script that orchestrates the entire update process
- **csv_to_json.py**: Converts sessions.csv to sessions.json
- **update_schedule.py**: Updates schedule.json from Excel data
- **fix_session_info_comprehensive.py**: Applies comprehensive fixes to session data
- **sync_session_data.py**: Synchronizes data between sessions.json and schedule.json
- **verify_data_consistency.py**: Checks data consistency across files

## Example: Full Update Process

To process updates and ensure all data is consistent:

```bash
# Update source data (sessions.csv and/or session_schedule_by_slot.xlsx)
# Then run:
./update_all.sh
```

This will update all JSON files and ensure consistency across different views.
