import csv
import json
import html
import sys
import os
import re # Import regular expressions for tag finding

def generate_tags(title, description_text): 
    """
    Analyzes title and description to generate relevant tags based on keywords.

    Parameters:
    - title: Session title string
    - description_text: Plain text session description string

    Returns:
    - A list of identified tags (strings), sorted alphabetically.
    """
    tags = set()
    # Combine title and description, convert to lowercase for case-insensitive matching
    full_text = (title + " " + description_text).lower()

    # Define keywords and corresponding tags - Updated based on CSV analysis
    # Keywords should be lowercase
    tag_keywords = {
        'AI': ['ai', 'artificial intelligence', 'gpt', 'llm', 'large language model',
               'chatgpt', 'claude', 'gemini', 'prompt', 'prompt design',
               'prompt engineering', 'chatbot', 'bot', 'generative ai', 'ai literacy'],
        'Pedagogy': ['pedagogy', 'teaching', 'learning', 'instruction', 'educator',
                     'classroom', 'student engagement', 'inquiry-based', 'lesson plan',
                     'learning science', 'place-based learning', 'cognitive load',
                     'self determination theory', 'experiential learning', 'constructivist',
                     'active learning', 'skill development'],
        'Humanities': ['humanities', 'literature', 'history', 'english', 'writing',
                       'text', 'reading', 'ethical history', 'literacy', 'close reading',
                       'philosophy'],
        'Writing': ['writing', 'composition', 'prose', 'essay', 'rhetorical', 'syntax',
                    'academic writing', 'writing assignment'],
        'Ethics': ['ethic', 'ethical', 'values', 'dignity', 'manipulation',
                   'dependency', 'slavery', 'digital citizenship', 'academic integrity',
                   'plagiarism', 'ai policy', 'appropriate use'],
        'Innovation': ['innovation', 'future', 'next era', 'emerging', 'transformative',
                       'customizing', 'rebooting'],
        'Student Engagement': ['student engagement', 'buy-in', 'participation',
                               'collaboration', 'immersive', 'experience', 'student agency',
                               'motivation'],
        'Curriculum': ['curriculum', 'lesson planning', 'assessment', 'ungrading',
                       'course design', 'unit plan', 'framework', 'assignments', 'syllabus'],
        'Assessment': ['assessment', 'grading', 'ungrading', 'feedback', 'evaluation',
                       'rubric', 'student work'],
        'Technology': ['technology', 'digital', 'tool', 'platform', 'simulations',
                       'online', 'apps', 'software', 'digital habits', 'screenagers'],
        'History': ['history', 'historical', 'primary sources'], # Added primary sources
        'Metacognition': ['metacognition', 'self-awareness', 'reflection',
                          'learning process', 'strategic learner'],
        'Simulations': ['simulation', 'investigation', 'role-playing', 'interactive',
                        'game-based learning'], # Added game-based
        'Wellbeing': ['dependency', 'connection', 'wellbeing', 'mental health',
                      'dopamine', 'human connection', 'digital dependency',
                      'screen time', 'student support'], # Added student support
        'Research': ['research', 'investigation', 'inquiry', 'data analysis',
                     'evidence'], # Added evidence
        'Collaboration': ['collaboration', 'collaborative', 'pair programming', 'co-lab',
                          'working group', 'community engagement', 'interschool',
                          'teamwork', 'group work'], # Added teamwork, group work
        'Professional Development': ['professional development', 'pd', 'teacher training',
                                     'communities of practice', 'faculty development',
                                     'teacher-led', 'lifelong learning'], # Added lifelong learning
        'Leadership': ['leadership', 'ai policy', 'school leadership', 'administration',
                       'strategic planning'], # Added admin, strategic planning
        'STEM': ['stem', 'science', 'programming', 'computer science'] # Added STEM explicitly
    }

    # Iterate through defined tags and their associated keywords
    for tag, keywords in tag_keywords.items():
        for keyword in keywords:
            # Use regex to find whole words to avoid partial matches (e.g., 'ai' in 'train')
            # re.escape handles special characters in keywords if any
            if re.search(r'\b' + re.escape(keyword) + r'\b', full_text):
                tags.add(tag)
                # Once a keyword for a tag is found, no need to check other keywords for the same tag
                break

    # Add strand-based tags automatically if not already present
    # Check title/description for strand info if not explicitly passed
    if 'strand 1' in full_text or 'ai in the classroom' in full_text:
         tags.add('AI')
         tags.add('Pedagogy')
    if 'strand 2' in full_text or 'human-centered innovation' in full_text:
         tags.add('Innovation')
         # Ethics is often linked, but let keyword matching handle it unless explicit
         # tags.add('Ethics')
    if 'strand 3' in full_text or 'leadership in ai' in full_text:
         tags.add('Leadership')
         tags.add('AI')


    # Return the sorted list of unique tags
    return sorted(list(tags))


def csv_to_json(csv_file, output_file='sessions.json'):
    """
    Convert CSV file with session data to JSON format for the symposium website,
    including time blocks and generated tags.

    Parameters:
    - csv_file: Path to CSV file
    - output_file: Path to save the JSON output (default: sessions.json)
    """
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        return False

    sessions = [] # List to hold processed session dictionaries

    try:
        # Open CSV file with utf-8-sig encoding to handle potential Byte Order Mark (BOM)
        with open(csv_file, mode='r', encoding='utf-8-sig') as f:
            print(f"Processing CSV file: {csv_file}")
            # Use DictReader for easy access to columns by header name
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

            # Check if headers exist
            if not fieldnames:
                print("Warning: CSV file appears to be empty or has no headers.")
                return False

            print(f"Detected Headers: {fieldnames}")

            # Normalize headers (lowercase, strip whitespace) for robust matching
            # Stores mapping from normalized name to original header name
            normalized_headers = {h.strip().lower(): h for h in fieldnames}
            print(f"Normalized Headers Keys: {list(normalized_headers.keys())}")

            # --- Function to find the original header name based on possible normalized names ---
            def find_header(possible_names):
                """Helper function to find the correct header name from a list of possibilities."""
                for name in possible_names:
                    if name in normalized_headers:
                        print(f"  Found header '{normalized_headers[name]}' for possible name '{name}'")
                        return normalized_headers[name] # Return the original header name
                print(f"  Warning: Could not find header for any of {possible_names}")
                return None
            # --- End Helper Function ---

            # --- Identify column headers using the helper function ---
            print("\n--- Identifying Headers ---")
            presenter_header = find_header(['presenter', 'presenter name', 'speaker', 'name', 'name2']) # Added name2
            school_header = find_header(['school', 'institution', 'organization', 'affiliation', 'school or organization']) # Added school or organization
            email_header = find_header(['email', 'email address', 'e-mail address']) # Added e-mail address
            title_header = find_header(['session title', 'title', 'presentation title'])
            description_header = find_header(['session description', 'description', 'abstract', 'details'])
            strand_header = find_header(['strand', 'track', 'category', 'which strand will your presentation be in?']) # Added specific question
            type_header = find_header(['session type', 'type', 'format', 'what is the format of your session?']) # Added specific question
            time_block_header = find_header(['time block', 'timeblock', 'block', 'session block', 'time'])
            location_header = find_header(['location', 'room', 'venue'])
            print("--- Finished Identifying Headers ---\n")
            # --- End Identifying Headers ---

            row_count = 0
            valid_session_count = 0

            # Process each row in the CSV file
            for row in reader:
                row_count += 1
                print(f"\n--- Processing Row {row_count} ---")

                # --- Extract data using identified headers ---
                # Use .get(header, '') to safely get data even if header wasn't found
                presenter_name = row.get(presenter_header, '').strip() if presenter_header else ''
                presenter_school = row.get(school_header, '').strip() if school_header else ''
                email = row.get(email_header, '').strip() if email_header else 'anonymous' # Default email if missing
                title = row.get(title_header, f'Untitled Session {row_count}').strip() if title_header else f'Untitled Session {row_count}'
                description = row.get(description_header, 'Description forthcoming.').strip() if description_header else 'Description forthcoming.'
                strand_value = row.get(strand_header, '').strip() if strand_header else ''
                session_type_value = row.get(type_header, '').strip() if type_header else ''
                time_block_value = row.get(time_block_header, '').strip() if time_block_header else ''
                location = row.get(location_header, 'TBD').strip() if location_header else 'TBD'
                # --- End Data Extraction ---

                # Print raw extracted values for debugging
                print(f"  Raw Title: {title[:50]}...") # Print first 50 chars
                print(f"  Raw Presenter: {presenter_name}")
                print(f"  Raw School: {presenter_school}")
                print(f"  Raw Strand: {strand_value}")
                print(f"  Raw Type: {session_type_value}")
                print(f"  Raw Time Block: {time_block_value}")
                print(f"  Raw Location: {location}")

                # --- Process Extracted Data ---

                # Process Strand
                strand = 'strand1' # Default value
                strand_name = '1: AI in the Classroom'
                if strand_value:
                    strand_lower = strand_value.lower()
                    if '1' in strand_value or 'ai' in strand_lower or 'classroom' in strand_lower:
                        strand = 'strand1'
                        strand_name = '1: AI in the Classroom'
                    elif '2' in strand_value or 'human' in strand_lower or 'innovation' in strand_lower:
                        strand = 'strand2'
                        strand_name = '2: Human-Centered Innovation'
                    elif '3' in strand_value or 'leadership' in strand_lower: # Added Strand 3 check
                        strand = 'strand3'
                        strand_name = '3: Leadership in AI'
                    else:
                         print(f"  Warning: Unknown strand value '{strand_value}', defaulting to Strand 1.")
                print(f"  Processed Strand: {strand} ({strand_name})")

                # Process Session Type
                type_class = 'type-workshop' # Default value
                type_name = 'Workshop'
                if session_type_value:
                    type_lower = session_type_value.lower()
                    # Check for combinations first (e.g., Presentation / Discussion)
                    if 'presentation' in type_lower and 'discussion' in type_lower:
                         type_class = 'type-presentation' # Prioritize presentation? Or create combined? Let's stick to main types.
                         type_name = 'Presentation and Q&A' # Or 'Presentation / Discussion'
                    elif 'workshop' in type_lower and 'discussion' in type_lower:
                         type_class = 'type-workshop'
                         type_name = 'Workshop' # Or 'Workshop / Discussion'
                    elif 'workshop' in type_lower:
                        type_class = 'type-workshop'
                        type_name = 'Workshop'
                    elif 'presentation' in type_lower or 'q&a' in type_lower:
                        type_class = 'type-presentation'
                        type_name = 'Presentation and Q&A'
                    elif 'discussion' in type_lower:
                        type_class = 'type-discussion'
                        type_name = 'Facilitated Discussion'
                    else:
                        print(f"  Warning: Unknown session type '{session_type_value}', defaulting to Workshop.")
                print(f"  Processed Type: {type_class} ({type_name})")

                # Process Presenter String
                if presenter_name and presenter_school:
                    # Check if there are multiple presenters separated by commas
                    presenter_names = [name.strip() for name in presenter_name.split(',')]
                    presenter_schools = [school.strip() for school in presenter_school.split(',')]

                    # If there are multiple names but only one school, assign the same school to all names
                    if len(presenter_names) > 1 and len(presenter_schools) == 1:
                        presenter_schools *= len(presenter_names)

                    # Combine names and schools in order
                    presenter = ', '.join(
                        f"{name} - {school}" for name, school in zip(presenter_names, presenter_schools)
                    )
                else:
                    # Use whichever value is available, or default to TBD
                    presenter = presenter_name or presenter_school or "TBD"
                print(f"  Processed Presenter: {presenter}")

                # Process Description for HTML and Preview
                description_cleaned = re.sub(r'\s+', ' ', description).strip()  # Collapse all whitespace
                description_escaped = html.escape(description_cleaned)
                description_html = description_escaped.replace('\n', '<br>')
                if not description_html:
                     description_html = "Description forthcoming."
                
                # Create preview from the original description text (first 150 chars)
                preview_text = ' '.join(description.split())  # Collapse all whitespace for cleaner preview
                preview = preview_text[:150].strip() + ("..." if len(preview_text) > 150 else "")
                print(f"  Processed Preview: {preview[:50]}...")

                # Process Time Block - Extract just the number (1, 2, or 3) if present
                time_block_processed = 'TBD' # Default value
                if time_block_value:
                     # Search for a digit 1, 2, or 3 bounded by non-word characters (or start/end)
                     match = re.search(r'\b([1-3])\b', time_block_value)
                     if match:
                          time_block_processed = match.group(1) # Get the matched digit
                     else:
                          print(f"  Warning: Could not extract block number (1, 2, or 3) from '{time_block_value}', setting to TBD.")
                print(f"  Processed Time Block: {time_block_processed}")

                # Generate Tags using the function defined above
                # Pass the original (unprocessed) description for better keyword context
                tags = generate_tags(title, description)
                print(f"  Generated Tags: {tags}")

                # --- Create final session dictionary ---
                session = {
                    "strand": strand,
                    "strandName": strand_name,
                    "type": type_class,
                    "typeName": type_name,
                    "title": html.escape(title), # Escape title just in case of stray HTML chars
                    "presenter": html.escape(presenter),
                    "email": html.escape(email), # Should be safe, but escape anyway
                    "preview": html.escape(preview), # Escape preview text
                    "description": description_html, # Already HTML formatted and escaped
                    "timeBlock": time_block_processed, # Use processed time block number
                    "location": html.escape(location),
                    "tags": tags # Add the generated tags list
                }
                # --- End Session Dictionary Creation ---

                sessions.append(session) # Add the processed session to the list
                valid_session_count += 1
                print(f"--> Successfully processed session: {title[:50]}...")

        # --- Post-Processing ---
        if not sessions:
            print("\nError: No valid sessions were processed from the CSV file.")
            return False

        # Write the list of session dictionaries to the JSON output file
        with open(output_file, 'w', encoding='utf-8') as f:
            # Use indent=2 for readability, ensure_ascii=False for proper character handling
            json.dump(sessions, f, indent=2, ensure_ascii=False)

        print(f"\n--- Conversion Summary ---")
        print(f"Total rows processed: {row_count}")
        print(f"Valid sessions created: {valid_session_count}")
        print(f"JSON file saved to: {output_file}")
        # --- End Post-Processing ---

    except FileNotFoundError:
        print(f"Error: File not found at {csv_file}")
        return False
    except Exception as e:
        # Catch any other unexpected errors during processing
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc() # Print detailed traceback for debugging
        return False

    return True # Indicate successful completion

# --- Main execution block ---
if __name__ == "__main__":
    # Check if CSV file path is provided as a command-line argument
    if len(sys.argv) < 2:
        # If not provided, try to find a default 'sessions.csv' in the current directory
        default_csv = 'sessions.csv'
        if os.path.exists(default_csv):
             csv_file_path = default_csv
             print(f"No CSV file specified, found default: {csv_file_path}")
        else:
             # If no argument and no default file, print usage instructions and exit
             print("\nUsage: python csv_to_json.py <path_to_csv_file> [output_json_file]")
             print(f"Example: python csv_to_json.py {default_csv}")
             print("Error: Please provide the path to the CSV file as the first argument.")
             sys.exit(1) # Exit with an error code
    else:
        # Use the path provided in the first command-line argument
        csv_file_path = sys.argv[1]

    # Determine the output JSON file path (use argument 2 if provided, else default)
    output_file_path = sys.argv[2] if len(sys.argv) > 2 else 'sessions.json'

    # Run the conversion process
    print(f"\nStarting conversion from '{csv_file_path}' to '{output_file_path}'...")
    if csv_to_json(csv_file_path, output_file_path):
        print("\nConversion completed successfully!")
    else:
        print("\nConversion failed.")
        sys.exit(1) # Exit with an error code if conversion failed
# --- End Main Execution ---
