"""
Simplified script to debug data processing issues
"""

import pandas as pd
import json
import sys

def main():
    print("Starting debug script...")
    
    # Try different encoding options for CSV
    csv_encodings = ['utf-8', 'latin1', 'cp1252', 'ISO-8859-1']
    
    for encoding in csv_encodings:
        try:
            print(f"Trying to read CSV with encoding: {encoding}")
            sessions_csv = pd.read_csv('sessions.csv', encoding=encoding)
            print(f"  Success! Read {len(sessions_csv)} rows with encoding {encoding}")
            print(f"  CSV columns: {sessions_csv.columns.tolist()}")
            break
        except Exception as e:
            print(f"  Failed with encoding {encoding}: {str(e)}")
    
    try:
        print("\nReading Excel file...")
        schedule_excel = pd.read_excel('schedule_by_id.xlsx')
        print(f"  Success! Read {len(schedule_excel)} rows")
        print(f"  Excel columns: {schedule_excel.columns.tolist()}")
    except Exception as e:
        print(f"  Failed to read Excel: {str(e)}")
    
    print("\nScript completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
