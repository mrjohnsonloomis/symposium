# Symposium Data Management System

This system manages session data for the symposium through a centralized workflow using a master JSON file.

## Overview

The system uses the following data flow:
1. Session information is stored in `sessions.csv` with a unique `sessionID` field.
2. Room and time assignments are stored in `schedule_by_id.xlsx`.
3. These are combined by `generate_master_sessions.py` to create a master `sessions.json` file. This script processes multiple occurrences of the same session into a single entry with an `occurrences` array. It also filters to include only specified strands (e.g., Strand 1 and Strand 2).
4. The HTML files (`schedule.html`, `index.html`, and `calendar.html`) fetch and parse data directly from `sessions.json` using client-side JavaScript.

## Key Files

- **Data Sources**:
  - `sessions.csv` - Contains all session details including title, description, presenter, etc.
  - `schedule_by_id.xlsx` - Contains room assignments and time slots using session IDs.

- **Master Data**:
  - `sessions.json` - The single source of truth for session data, consumed directly by the HTML pages. It features an `occurrences` array for sessions that appear in multiple time slots/locations.

- **HTML Pages**:
  - `schedule.html` - The schedule view, dynamically loads data from `sessions.json`.
  - `index.html` - The main page showing session cards, dynamically loads data from `sessions.json`.
  - `calendar.html` - The calendar view, dynamically loads data from `sessions.json`.

## Scripts

### Primary Update Script
- `update_all_from_json.sh` - Master script that runs the data generation and verification steps.

### Component Scripts
- `generate_master_sessions.py` - Creates the master `sessions.json` from `sessions.csv` and `schedule_by_id.xlsx`.
- `update_schedule_from_json.py` - Verifies `sessions.json` structure (previously updated `schedule.html`).
- `update_index_from_json.py` - Verifies `sessions.json` structure (previously updated `index.html`).
- `update_calendar_from_json.py` - Verifies `sessions.json` structure (previously updated `calendar.html`).
- `verify_data_consistency.py` - Checks for consistency between `sessions.csv`, `schedule_by_id.xlsx`, and the generated `sessions.json`.

## How to Use

1. **Update Session Information**:
   - Edit `sessions.csv` to add or modify session information.
   - Ensure each session has a unique `sessionID`.

2. **Update Schedule Information**:
   - Edit `schedule_by_id.xlsx` to assign rooms and time slots to sessions using their `sessionID`s.
   - Special events (like registration, keynote, etc.) can be included.

3. **Generate Data and Verify**:
   - Run `./update_all_from_json.sh` to:
     - Create/update the master `sessions.json`.
     - Run verification scripts.
   - Test `index.html`, `schedule.html`, and `calendar.html` in a browser, preferably with a local HTTP server.

## Data Structure

### sessions.json Format
Each entry in `sessions.json` can be a regular session or a special event.

**Regular Session Example (with multiple occurrences):**
```json
{
  "id": "S101",
  "strand": "strand1",
  "strandName": "1: AI in the Classroom",
  "type": "workshop",
  "typeName": "Workshop",
  "title": "Advanced AI Workshop",
  "presenter": "Presenter Name",
  "email": "presenter@example.com",
  "organization": "Organization Name",
  "description": "Full session description...",
  "preview": "Short preview...",
  "tags": ["AI", "Advanced", "Pedagogy"],
  "isSpecialEvent": false,
  "occurrences": [
    {
      "occurrenceId": "S101_occ1", // Optional unique ID for the occurrence
      "timeBlock": "10:15 - 11:15",
      "timeSlotGroup": "1", // e.g., "1", "2", "3"
      "location": "Room A"
    },
    {
      "occurrenceId": "S101_occ2",
      "timeBlock": "13:30 - 14:30",
      "timeSlotGroup": "2",
      "location": "Room B"
    }
  ]
}
```

**Special Event Example:**
```json
{
  "id": "EVT01",
  "title": "Registration",
  "timeBlock": "08:00 - 09:00",
  "location": "Lobby",
  "isSpecialEvent": true,
  "occurrences": [ // Special events also use occurrences for consistency, even if usually single
    {
      "timeBlock": "08:00 - 09:00",
      "location": "Lobby"
    }
  ]
  // Other fields like strand, type, presenter are typically null or absent for special events
}
```
- `id`: Unique identifier for the session.
- `strand`, `strandName`: Strand information.
- `type`, `typeName`: Session type information.
- `title`, `presenter`, `email`, `organization`, `description`, `preview`, `tags`: Standard session details.
- `isSpecialEvent`: Boolean, true if it's a non-session event like "Lunch" or "Registration".
- `occurrences`: An array of objects, where each object defines a specific time and location for the session. This allows a single session entry to represent multiple scheduled instances.
    - `occurrenceId`: An optional unique ID for this specific instance.
    - `timeBlock`: The time slot for this occurrence (e.g., "10:15 - 11:15").
    - `timeSlotGroup`: A numerical or categorical grouping for the time block (e.g., "1", "2", "3").
    - `location`: The room or location for this occurrence.

## Troubleshooting

If the update process or data display fails:
1. Check that `sessions.csv` has valid `sessionID`s and correct data.
2. Verify that `schedule_by_id.xlsx` references valid `sessionID`s and has complete time/location data for scheduled sessions.
3. Look for encoding issues in `sessions.csv`.
4. Ensure `generate_master_sessions.py` is correctly processing and merging data, especially the `occurrences`.
5. Check browser console for errors when viewing HTML pages (network errors for `sessions.json`, JavaScript errors in parsing/rendering).
6. Use `verify_data_consistency.py` to pinpoint discrepancies.
