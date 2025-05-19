import pandas as pd

# Read the Excel files
try:
    schedule_by_id = pd.read_excel('schedule_by_id.xlsx')
    print("=== schedule_by_id.xlsx ===")
    print(schedule_by_id.head())
    print("\nColumns:", schedule_by_id.columns.tolist())
except Exception as e:
    print(f"Error reading schedule_by_id.xlsx: {e}")

try:
    session_schedule_by_slot = pd.read_excel('session_schedule_by_slot.xlsx')
    print("\n=== session_schedule_by_slot.xlsx ===")
    print(session_schedule_by_slot.head())
    print("\nColumns:", session_schedule_by_slot.columns.tolist())
except Exception as e:
    print(f"Error reading session_schedule_by_slot.xlsx: {e}")

# Check the current sessions.json structure
try:
    sessions_json = pd.read_json('sessions.json')
    print("\n=== sessions.json structure ===")
    if isinstance(sessions_json, pd.DataFrame):
        print(sessions_json.head())
        print("\nColumns:", sessions_json.columns.tolist())
    else:
        print("Not a standard DataFrame structure")
except Exception as e:
    print(f"Error reading sessions.json: {e}")
