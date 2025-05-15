import pandas as pd
import json
import re

df = pd.read_excel('session_schedule_by_slot.xlsx')
print('Looking for session "Student Buy-In and Ungrading" in Excel:')
for _, row in df.iterrows():
    for col in df.columns[1:]:
        val = row[col]
        if not pd.isna(val) and 'Buy' in str(val):
            print(f'- Found in {row["Time Slot"]}, {col}: {val}')

# Also look for the Deeper Dive session
print('\nLooking for "Deeper Dive" sessions:')
for _, row in df.iterrows():
    for col in df.columns[1:]:
        val = row[col]
        if not pd.isna(val) and 'Deeper Dive' in str(val):
            print(f'- Found in {row["Time Slot"]}, {col}: {val}')

# Check the title matching function
print('\nChecking the title matching function against sessions.json:')
with open('sessions.json', 'r') as f:
    sessions = json.load(f)

def find_session_by_title(sessions, title):
    """Find a session in the sessions list by title (or partial title match)"""
    # Remove any presenter or custom notation from the title
    clean_title = re.sub(r'(.+?):\s*', '', title).strip()
    
    # Normalize quotes - replace different types of quotes with simple double quotes
    clean_title = clean_title.replace('"', '"').replace('"', '"').replace('&quot;', '"')
    
    print(f"Looking for title: '{title}', cleaned to: '{clean_title}'")
    
    # Print all titles from sessions for debugging
    print("Available session titles:")
    for session in sessions:
        session_title = session.get('title', '')
        normalized_title = session_title.replace('"', '"').replace('"', '"').replace('&quot;', '"')
        print(f"  - '{session_title}' normalized to '{normalized_title}'")
    
    # First try exact match with normalized quotes
    for session in sessions:
        session_title = session.get('title', '')
        normalized_title = session_title.replace('"', '"').replace('"', '"').replace('&quot;', '"')
        
        if normalized_title == clean_title:
            print(f"Found exact match: {session_title}")
            return session
    
    # Then try partial match (title might be truncated in Excel)
    for session in sessions:
        session_title = session.get('title', '')
        normalized_title = session_title.replace('"', '"').replace('"', '"').replace('&quot;', '"')
        
        if clean_title and normalized_title and (clean_title in normalized_title or normalized_title in clean_title):
            print(f"Found partial match: {session_title}")
            return session
    
    print("No match found")
    return None

# Test with some actual titles from the Excel sheet
titles_to_test = [
    "Cotton: Student Buy-in and Ungrading in the Humanities Classroom",
    "Student Buy-In and \"Ungrading\" in the Humanities Classroom"
]

for title in titles_to_test:
    session = find_session_by_title(sessions, title)
    if session:
        print(f"Found session: {session.get('title')} by {session.get('presenter')}")
    else:
        print(f"No session found for '{title}'")
