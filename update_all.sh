#!/bin/bash
# This script updates both sessions.json and schedule.json from their respective source files

echo "Updating sessions data from CSV..."
python3 csv_to_json.py sessions.csv sessions.json

echo ""
echo "Updating schedule data from Excel..."
python3 update_schedule.py

# Also update the schedule.json for the calendar view
python3 excel_to_schedule.py

# Update session locations with room assignments
echo ""
echo "Updating room assignments..."
python3 update_rooms.py

echo ""
echo "All data has been updated!"
