#!/bin/sh
echo "=== Testing our fixes ==="
echo "Let's check if the problematic sessions display correctly now:"
echo ""
echo "Searching for sessions with quotes in titles:"
cd /workspaces/symposium && grep -n '"' sessions.json

echo ""
echo "Opening the website to see how it displays:"
echo "Please check the browser to verify the fix worked."
