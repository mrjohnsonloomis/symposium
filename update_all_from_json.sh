#!/bin/bash

# Master script to update all HTML files from sessions.json

echo "=== Master Update Process ==="

echo "Step 1: Generating sessions.json from CSV and Excel data..."
python3 generate_master_sessions.py

echo ""
echo "Step 2: Verifying sessions.json (schedule, index, calendar scripts now only verify)..."
python3 update_schedule_from_json.py
python3 update_index_from_json.py
python3 update_calendar_from_json.py

echo ""
echo "Step 3: Verifying data consistency across sources (optional but recommended)..."
python3 verify_data_consistency.py

echo ""
echo "Master update process complete. sessions.json is the single source of truth for HTML pages."
