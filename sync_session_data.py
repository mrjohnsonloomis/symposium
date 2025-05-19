#!/usr/bin/env python3
"""
Advanced synchronization script to ensure complete consistency between:
- sessions.json (used by session cards in index.html)
- schedule.json (used by schedule.html and calendar.html)

This script prioritizes schedule.json's room and time slot assignments
and updates sessions.json accordingly, while preserving other session details.
"""

import json
import sys
import re
from difflib import SequenceMatcher

def similarity(a, b):
    """Calculate the similarity ratio between two strings"""
    return SequenceMatcher(None, a, b).ratio()

def normalize_title(title):
    """Normalize a title for better matching"""
    if not title:
        return ""
    # Convert quotes and other special characters
    normalized = title.replace('&quot;', '"').replace('&#x27;', "'").replace('â€™', "'").replace('â€"', "-")
    # Remove punctuation variations
    normalized = re.sub(r'[?!:;.,]', '', normalized).lower().strip()
    return normalized

def find_best_match(session, schedule_sessions, threshold=0.85):
    """Find the best matching session in schedule based on title similarity"""
    session_title = session.get('title', '')
    norm_session_title = normalize_title(session_title)
    
    best_match = None
    best_score = 0
    
    for schedule_session in schedule_sessions:
        schedule_title = schedule_session.get('title', '')
        norm_schedule_title = normalize_title(schedule_title)
        
        # Check for exact normalized match first
        if norm_session_title and norm_schedule_title and norm_session_title == norm_schedule_title:
            return schedule_session
        
        # Otherwise calculate similarity score
        score = similarity(norm_session_title, norm_schedule_title)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = schedule_session
    
    return best_match

def sync_sessions_with_schedule():
    print("Starting advanced synchronization of sessions.json with schedule.json...")
    
    try:
        # Load sessions.json
        with open('sessions.json', 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        print(f"Loaded sessions.json with {len(sessions)} entries")
        
        # Load schedule.json
        with open('schedule.json', 'r', encoding='utf-8') as f:
            schedule = json.load(f)
        print(f"Loaded schedule.json with {len(schedule.get('sessions', []))} session entries")
        
        # Extract all sessions from schedule.json
        schedule_sessions = schedule.get('sessions', [])
        
        # Create a mapping of session titles to their time slots and rooms
        schedule_info = {}
        for s in schedule_sessions:
            time_slot = s.get('timeSlot', '')
            room = s.get('room', '')
            title = s.get('title', '')
            presenter = s.get('presenter', '')
            
            if title:
                # Some sessions appear in multiple time slots
                if title not in schedule_info:
                    schedule_info[title] = []
                
                schedule_info[title].append({
                    'timeSlot': time_slot,
                    'room': room,
                    'presenter': presenter
                })
        
        print(f"Loaded {len(sessions)} sessions and {len(schedule_sessions)} scheduled sessions")
        
        # Update sessions.json with schedule information
        updates_made = 0
        skipped_sessions = []
        
        for session in sessions:
            session_title = session.get('title', '')
            
            # Find matching session in schedule
            best_match = find_best_match(session, schedule_sessions)
            
            if best_match:
                matched_title = best_match.get('title', '')
                schedule_time_slot = best_match.get('timeSlot', '')
                schedule_room = best_match.get('room', '')
                schedule_presenter = best_match.get('presenter', '')
                
                # Update time block if needed
                if schedule_time_slot and (session.get('timeBlock', '') == 'TBD' or not session.get('timeBlock')):
                    session['timeBlock'] = schedule_time_slot
                    print(f"Updated timeBlock for '{session_title[:50]}...': '{session.get('timeBlock', 'None')}' → '{schedule_time_slot}'")
                    updates_made += 1
                
                # Update location if needed
                if schedule_room and (session.get('location', '') == 'TBD' or 
                                     session.get('location', '') == 'anonymous' or 
                                     not session.get('location')):
                    session['location'] = schedule_room
                    print(f"Updated location for '{session_title[:50]}...': '{session.get('location', 'None')}' → '{schedule_room}'")
                    updates_made += 1
                
                # Update presenter in schedule if needed
                if session.get('presenter') and not schedule_presenter:
                    # This needs to be done separately in the schedule.json update below
                    pass
            else:
                print(f"WARNING: Could not find matching schedule entry for '{session_title[:50]}...'")
                skipped_sessions.append(session_title)
        
        # Also check for missing sessions in sessions.json that are in schedule.json
        known_session_titles = [normalize_title(s.get('title', '')) for s in sessions]
        missing_sessions = []
        
        for schedule_session in schedule_sessions:
            schedule_title = schedule_session.get('title', '')
            norm_schedule_title = normalize_title(schedule_title)
            
            if norm_schedule_title and not any(similarity(norm_schedule_title, t) > 0.85 for t in known_session_titles if t):
                # Skip generic titles like "Arrival & Registration"
                if "arrival" not in norm_schedule_title.lower() and "keynote" not in norm_schedule_title.lower() and "closing" not in norm_schedule_title.lower():
                    missing_sessions.append(schedule_title)
        
        # Now update the schedule.json with correct presenter information
        schedule_updates = 0
        
        for schedule_session in schedule_sessions:
            schedule_title = schedule_session.get('title', '')
            schedule_presenter = schedule_session.get('presenter', '')
            
            # Find matching session in sessions.json
            best_match = None
            for session in sessions:
                session_title = session.get('title', '')
                if similarity(normalize_title(schedule_title), normalize_title(session_title)) > 0.85:
                    best_match = session
                    break
            
            if best_match:
                session_presenter = best_match.get('presenter', '')
                
                # Update presenter in schedule if needed
                if session_presenter and not schedule_presenter:
                    schedule_session['presenter'] = session_presenter
                    print(f"Updated presenter in schedule.json for '{schedule_title[:50]}...': '' → '{session_presenter}'")
                    schedule_updates += 1
        
        # Save updated sessions.json
        with open('sessions.json', 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
        
        # Save updated schedule.json
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)
        
        print(f"\nSynchronization completed with {updates_made} updates to sessions.json")
        print(f"Made {schedule_updates} presenter updates to schedule.json")
        
        if skipped_sessions:
            print(f"\nWARNING: {len(skipped_sessions)} sessions could not be matched to schedule entries:")
            for i, title in enumerate(skipped_sessions[:5], 1):
                print(f"  {i}. {title[:100]}")
            if len(skipped_sessions) > 5:
                print(f"  ...and {len(skipped_sessions) - 5} more")
        
        if missing_sessions:
            print(f"\nNOTE: Found {len(missing_sessions)} schedule entries without matching sessions.json entries:")
            for i, title in enumerate(missing_sessions[:5], 1):
                print(f"  {i}. {title[:100]}")
            if len(missing_sessions) > 5:
                print(f"  ...and {len(missing_sessions) - 5} more")
        
        return True
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if sync_sessions_with_schedule():
        sys.exit(0)
    else:
        sys.exit(1)
