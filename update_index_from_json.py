"""
Update index.html based on the master sessions.json file
"""

import json
import re
import os
from bs4 import BeautifulSoup

def main():
    print("Updating index.html from sessions.json...")
    
    try:
        # Load the sessions.json file
        with open('sessions.json', 'r', encoding='utf-8') as f:
            sessions = json.load(f)
            
        print(f"Loaded {len(sessions)} sessions from sessions.json")
        
        # Filter out special events
        regular_sessions = [s for s in sessions if not s.get('isSpecialEvent', False)]
        
        # Load the index.html file
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the session cards container
        cards_container = soup.find('div', id='sessions-container')
        if not cards_container:
            print("Error: Could not find sessions container in index.html")
            return 1
            
        # Clear the existing content
        cards_container.clear()
        
        # Add all regular sessions as cards
        for session in regular_sessions:
            # Create a session card
            card = soup.new_tag('div', attrs={
                'class': f"session-card {session.get('strand', '')}",
                'data-strand': session.get('strand', ''),
                'data-type': session.get('type', '')
            })
            
            # Add title
            title_div = soup.new_tag('div', attrs={'class': 'session-title'})
            title_div.string = session.get('title', '')
            card.append(title_div)
            
            # Add presenter
            presenter = session.get('presenter', '')
            if presenter:
                presenter_div = soup.new_tag('div', attrs={'class': 'session-presenter'})
                presenter_div.string = presenter
                card.append(presenter_div)
            
            # Add preview
            preview = session.get('preview', '')
            if preview:
                preview_div = soup.new_tag('div', attrs={'class': 'session-preview'})
                preview_div.string = preview
                card.append(preview_div)
            
            # Add time and room if available
            time_block = session.get('timeBlock', '')
            location = session.get('location', '')
            if time_block and location:
                time_room_div = soup.new_tag('div', attrs={'class': 'session-time-room'})
                time_room_div.string = f"{time_block} | {location}"
                card.append(time_room_div)
            
            # Add tags
            tags = session.get('tags', [])
            if tags:
                tags_div = soup.new_tag('div', attrs={'class': 'session-tags'})
                for tag in tags:
                    tag_span = soup.new_tag('span', attrs={'class': 'tag'})
                    tag_span.string = tag
                    tags_div.append(tag_span)
                card.append(tags_div)
            
            # Add the card to the container
            cards_container.append(card)
        
        # Write the updated HTML back to file
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        print("Successfully updated index.html")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    main()
