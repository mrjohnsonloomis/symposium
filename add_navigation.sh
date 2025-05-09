#!/bin/bash
# This script adds navigation tabs to index.html

# Check if the file exists
if [ ! -f "index.html" ]; then
  echo "Error: index.html not found!"
  exit 1
fi

# Create a temporary file
temp_file=$(mktemp)

# Add navigation tabs after the header section
awk '
/<\/header>/ {
  print $0
  print ""
  print "    <div class=\"container py-4\">"
  print "        <div class=\"row mb-4\">"
  print "            <div class=\"col-12\">"
  print "                <ul class=\"nav nav-tabs\">"
  print "                    <li class=\"nav-item\">"
  print "                        <a class=\"nav-link active\" href=\"index.html\">Session Listing</a>"
  print "                    </li>"
  print "                    <li class=\"nav-item\">"
  print "                        <a class=\"nav-link\" href=\"schedule.html\">Schedule</a>"
  print "                    </li>"
  print "                </ul>"
  print "            </div>"
  print "        </div>"
  next
}
/<div class="container py-4">/ {
  print "    <div class=\"container py-4\">"
  print "        <div class=\"row\">"
  next
}
{print}
' index.html > "$temp_file"

# Replace the original file with the modified content
mv "$temp_file" index.html

echo "Navigation tabs added to index.html"
