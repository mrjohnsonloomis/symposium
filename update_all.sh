#!/bin/bash
# This script updates all data files (sessions.json, schedule.json) and ensures calendar view is updated

echo "=== Starting comprehensive update process ==="

echo "Step 1: Updating sessions data from CSV..."
python3 csv_to_json.py sessions.csv sessions.json

echo ""
echo "Step 2: Updating schedule data from Excel..."
python3 update_schedule.py

echo ""
echo "Step 3: Updating calendar schedule data..."
python3 excel_to_schedule.py

echo ""
echo "Step 4: Updating room assignments in all data files..."
python3 update_rooms.py

echo ""
echo "Step 5: Updating sessions with schedule information..."
python3 update_sessions.py

echo ""
echo "Step 6: Running comprehensive fixes for consistency..."
python3 fix_session_info_comprehensive.py

echo ""
echo "Step 7: Synchronizing data between sessions.json and schedule.json..."
python3 sync_session_data.py

echo ""
echo "Step 8: Applying specific fixes for David Nurenberg's session..."
python3 fix_nurenberg_session.py

echo ""
echo "Step 9: Running verification checks..."
python3 verify_data_consistency.py

echo ""
echo "=== Update process complete! ==="
echo "You can now view the updated data in:"
echo "- index.html (Session Listing)"
echo "- schedule.html (Schedule View)"
echo "- calendar.html (Calendar View)"
