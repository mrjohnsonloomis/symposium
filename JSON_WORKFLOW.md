# Symposium Data Management System

This system manages session data for the symposium through a centralized workflow using a master JSON file.

## Overview

The system uses the following data flow:
1. Session information is stored in `sessions.csv` with a unique `sessionID` field
2. Room and time assignments are stored in `schedule_by_id.xlsx`
3. These are combined to create a master `sessions.json` file
4. The HTML files (`schedule.html`, `index.html`, and `calendar.html`) are generated from the master JSON

## Key Files

- **Data Sources**:
  - `sessions.csv` - Contains all session details including title, description, presenter, etc.
  - `schedule_by_id.xlsx` - Contains room assignments and time slots using session IDs

- **Master Data**:
  - `sessions.json` - The primary data file that all HTML pages are generated from

- **HTML Pages**:
  - `schedule.html` - The schedule view showing sessions by time and room
  - `index.html` - The main page showing session cards
  - `calendar.html` - The calendar view of the schedule
  - `calendar_data.json` - Supporting data for the calendar view

## Scripts

### Primary Update Script
- `update_all_from_json.sh` - Master script that runs all the update steps

### Component Scripts
- `generate_master_sessions.py` - Creates the master `sessions.json` from `sessions.csv` and `schedule_by_id.xlsx`
- `update_schedule_from_json.py` - Updates `schedule.html` from `sessions.json`
- `update_index_from_json.py` - Updates `index.html` from `sessions.json`
- `update_calendar_from_json.py` - Updates `calendar.html` and creates `calendar_data.json` from `sessions.json`

## How to Use

1. **Update Session Information**:
   - Edit `sessions.csv` to add or modify session information
   - Ensure each session has a unique `sessionID`

2. **Update Schedule Information**:
   - Edit `schedule_by_id.xlsx` to assign rooms and time slots to sessions using their sessionIDs
   - Special events (like registration, keynote, etc.) can be included as text

3. **Generate Data and Update HTML**:
   - Run `./update_all_from_json.sh` to:
     - Create the master `sessions.json`
     - Update all HTML files

## Data Structure

### Sessions.json Format
Each session object in the JSON file includes:

```json
{
  "id": 1,
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
  "timeBlock": "10:15 - 11:15",
  "location": "Room Name",
  "tags": ["Tag1", "Tag2"],
  "isSpecialEvent": false
}
```

Special events have `isSpecialEvent: true` and typically don't have presenter information.

## Troubleshooting

If the update process fails:

1. Check that `sessions.csv` has valid sessionIDs
2. Verify that `schedule_by_id.xlsx` references valid sessionIDs
3. Look for encoding issues in the CSV file
4. Check for HTML structure changes that might break the update scripts
