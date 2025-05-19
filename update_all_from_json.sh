#!/bin/bash

# Master script to update all HTML files from sessions.json

echo "=== Master Update Process ==="

echo "Step 1: Generating sessions.json from CSV and Excel data..."
python3 generate_master_sessions.py

echo ""
echo "Step 2: Updating schedule.html..."
python3 update_schedule_from_json.py

echo ""
echo "Step 3: Updating index.html..."
python3 update_index_from_json.py

echo ""
echo "Step 4: Updating calendar.html..."
python3 update_calendar_from_json.py

echo ""
echo "=== All updates complete! ==="
