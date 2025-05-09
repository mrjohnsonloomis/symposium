#!/bin/bash

# Script to update the calendar view from the schedule data
# This is an extension of update_all.sh for the calendar view

echo "Updating schedule data from Excel file..."
python3 excel_to_schedule.py

echo "Process complete!"
echo "You can now view the updated calendar at calendar.html"
