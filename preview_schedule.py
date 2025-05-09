import pandas as pd

# Load the Excel file
try:
    df = pd.read_excel('/workspaces/symposium/session_schedule_by_slot.xlsx')
    
    # Print the column names
    print("Column names:")
    print(df.columns.tolist())
    
    # Print the first few rows to understand structure
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Get number of unique time slots and rooms
    if 'Time' in df.columns:
        print(f"\nUnique Time Slots: {df['Time'].nunique()}")
    
    if 'Room' in df.columns or 'Location' in df.columns:
        room_col = 'Room' if 'Room' in df.columns else 'Location'
        print(f"Unique Rooms: {df[room_col].nunique()}")
        
    # Print shape
    print(f"\nDataFrame shape: {df.shape}")
    
except Exception as e:
    print(f"Error reading Excel file: {e}")
