# Symposium Data Management System

This system manages session data for the symposium through a centralized workflow using a master JSON file.

## Overview

The system uses the following data flow:
1. Session information is stored in `sessions.csv` with a unique `sessionID` field.
2. Room and time assignments are stored in `schedule_by_id.xlsx`.
3. These are combined by `generate_master_sessions.py` to create a master `sessions.json` file.
4. The HTML files (`index.html`, `schedule.html`, and `calendar.html`) directly fetch and process `sessions.json` to display session data.

## Key Files

- **Data Sources**:
  - `sessions.csv` - Contains all session details including title, description, presenter, etc.
  - `schedule_by_id.xlsx` - Contains room assignments and time slots using session IDs.

- **Master Data**:
  - `sessions.json` - The single source of truth. This primary data file is fetched directly by all HTML pages.

- **HTML Pages**:
  - `index.html` - The main page showing filterable session cards. Fetches `sessions.json`.
  - `schedule.html` - The schedule view showing sessions by time and room. Fetches `sessions.json`.
  - `calendar.html` - The calendar view of the schedule. Fetches `sessions.json`.

- **Deprecated JSON Files (No Longer Used)**:
  - `calendar_data.json`
  - `schedule.json`

## Scripts

### Primary Update Script
- `update_all_from_json.sh` - Master script that runs all necessary update steps.

### Component Scripts
- `generate_master_sessions.py` - Creates the master `sessions.json` from `sessions.csv` and `schedule_by_id.xlsx`.
- `update_index_from_json.py` - Updates static content in `index.html` if necessary (though most data is now client-side rendered from `sessions.json`). This script might be simplified or deprecated further if `index.html` becomes fully dynamic.
- `update_schedule_from_json.py` - This script is now largely deprecated as `schedule.html` fetches `sessions.json` directly. It might retain minimal functionality or be removed.
- `update_calendar_from_json.py` - This script is now largely deprecated as `calendar.html` fetches `sessions.json` directly. It might retain minimal functionality or be removed.

## How to Use

1. **Update Session Information**:
   - Edit `sessions.csv` to add or modify session information.
   - Ensure each session has a unique `sessionID`.

2. **Update Schedule Information**:
   - Edit `schedule_by_id.xlsx` to assign rooms and time slots to sessions using their sessionIDs.
   - Special events (like registration, keynote, etc.) can be included.

3. **Generate Master Data File**:
   - Run `./update_all_from_json.sh`. This script will primarily execute `generate_master_sessions.py` to create/update `sessions.json`.
   - The HTML pages will automatically fetch the latest `sessions.json` when loaded or refreshed in a browser.

   > **Note**: The system supports sessions that appear in multiple time slots. A session that occurs more than once will have a unique ID for each occurrence beyond the first (e.g., "1_occurrence_2") in `sessions.json`, allowing each to be treated as a distinct entry.

## Data Structure

### sessions.json Format
Each session object in the `sessions.json` file includes the following (ensure your JavaScript in HTML files correctly references these property names, e.g., `time_slot` and `room`):

```json
{
  "id": "1", // String or Integer. For multiple occurrences, e.g., "1_occurrence_2".
  "strand": "strand1",
  "strandName": "1: AI in the Classroom",
  "type": "workshop",
  "typeName": "Workshop",
  "title": "Session Title",
  "presenter": "Presenter Name",
  "email": "presenter@example.com",
  "organization": "Organization Name",
  "description": "Full session description",
  "preview": "Short preview of the description",
  "time_slot": "10:15 - 11:15", // Property name for time slot
  "room": "Room Name",         // Property name for room/location
  "tags": ["Tag1", "Tag2"],
  "isSpecialEvent": false
}
```

Special events have `isSpecialEvent: true` and typically don't have presenter information.

## Troubleshooting

1.  **Data Not Appearing/Incorrect in HTML**: 
    *   Verify `sessions.json` exists in the `/workspaces/symposium/` directory and is correctly formatted (valid JSON).
    *   Check the browser's developer console (usually F12) in `index.html`, `schedule.html`, or `calendar.html` for any JavaScript errors related to fetching or parsing `sessions.json`.
    *   Ensure the JavaScript in each HTML file correctly references the property names used in `sessions.json` (e.g., `session.time_slot`, `session.room`).
    *   Confirm `generate_master_sessions.py` ran successfully and generated `sessions.json` with the expected data.
2.  **`generate_master_sessions.py` Errors**:
    *   Check that `sessions.csv` has valid `sessionID`s.
    *   Verify that `schedule_by_id.xlsx` references valid `sessionID`s from `sessions.csv`.
    *   Look for encoding issues in `sessions.csv`.
    *   Ensure correct sheet names are used if `generate_master_sessions.py` reads specific sheets from the Excel file.
