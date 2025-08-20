import json
import pandas as pd
import os
import glob
import numpy as np

def load_subjects_from_file(filename):
    """
    Loads subjects from a JSON file and returns them as a list of dictionaries.
    """
    # Construct the full path using os.path.join
    full_path = os.path.join('data', filename)
    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data 

def parse_subjects(subjects):
    """
    Parses a list of subjects, extracting comprehensive information for each.
    """
    parsed_subjects = []
    for subject in subjects:
        parsed_data = parse_subject_data(subject)
        # Convert numpy arrays to lists if present
        for key, value in parsed_data.items():
            if isinstance(value, np.ndarray):
                parsed_data[key] = value.tolist()
        parsed_subjects.append(parsed_data)
    return parsed_subjects

def parse_subject_data(subject_data):
    """
    Parses the API response and extracts a comprehensive set of information,
    including separating kanji readings into on'yomi and kun'yomi.
    """
    data = subject_data.get('data', {})
    subject_type = subject_data.get('object')
    
    # Common fields
    parsed_data = {
        'id': subject_data.get('id'),
        'object': subject_type,
        'url': subject_data.get('url'),
        'data_updated_at': subject_data.get('data_updated_at'),
        'created_at': data.get('created_at'),
        'level': data.get('level'),
        'slug': data.get('slug'),
        'hidden_at': data.get('hidden_at'),
        'document_url': data.get('document_url'),
        'characters': data.get('characters'),
        'meanings': [meaning['meaning'] for meaning in data.get('meanings', [])],
        'auxiliary_meanings': [aux['meaning'] for aux in data.get('auxiliary_meanings', [])],
        'lesson_position': data.get('lesson_position'),
        'spaced_repetition_system_id': data.get('spaced_repetition_system_id'),
        # Initialize onyomi and kunyomi to empty lists; will update for kanji
        'onyomi_readings': [],
        'kunyomi_readings': [],
        'primary_reading': None,  # Retaining this for compatibility
    }

    # Type-specific fields
    if subject_type in ['kanji', 'vocabulary']:
        readings = data.get('readings', [])
        parsed_data.update({
            'readings': [reading['reading'] for reading in readings],
            'component_subject_ids': data.get('component_subject_ids', []),
            'amalgamation_subject_ids': data.get('amalgamation_subject_ids', []),
            'visually_similar_subject_ids': data.get('visually_similar_subject_ids', []),
            'meaning_mnemonic': data.get('meaning_mnemonic'),
            'reading_mnemonic': data.get('reading_mnemonic', '')
        })

        # For kanji, separate on'yomi and kun'yomi readings
        if subject_type == 'kanji':
            parsed_data['onyomi_readings'] = [reading['reading'] for reading in readings if reading.get('type') == 'onyomi']
            parsed_data['kunyomi_readings'] = [reading['reading'] for reading in readings if reading.get('type') == 'kunyomi']
            
            # Extract primary reading if needed
            primary_readings = [reading['reading'] for reading in readings if reading.get('primary')]
            parsed_data['primary_reading'] = primary_readings[0] if primary_readings else None
    
    if subject_type == 'radical':
        parsed_data.update({
            'meaning_mnemonic': data.get('meaning_mnemonic'),
            'character_images': [image['url'] for image in data.get('character_images', [])]
        })

    if subject_type == 'vocabulary':
        parsed_data.update({
            'parts_of_speech': data.get('parts_of_speech', []),
            'context_sentences': [{'en': sentence['en'], 'ja': sentence['ja']} for sentence in data.get('context_sentences', [])],
            'pronunciation_audios': [audio['url'] for audio in data.get('pronunciation_audios', [])]
        })

    return parsed_data


def save_to_excel(parsed_subjects, output_filename):
    """
    Saves parsed subjects to an Excel file.
    """
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(parsed_subjects)
    
    # Construct the full path using os.path.join for the output file
    full_output_path = os.path.join('data', output_filename)
    
    # Save the DataFrame to an Excel file
    df.to_excel(full_output_path, index=False, engine='openpyxl')
    print(f"Data saved to {full_output_path}")

def find_latest_wanikani_file(directory):
    """
    Finds the latest file in the specified directory that starts with 'wanikani_subjects' and ends with '.json'.
    Returns the path of the first file found matching the pattern.
    """
    pattern = os.path.join(directory, 'wanikani_subjects*.json')
    files = glob.glob(pattern)
    if files:
        # Optionally, sort the files by modification time in descending order and return the first one
        # This ensures that if there are multiple files, the most recent one is returned
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    else:
        print("No matching files found.")
        return None
    
def save_data(parsed_subjects, output_filename, format='excel'):
    """
    Saves parsed subjects to a file in the specified format.
    """
    df = pd.DataFrame(parsed_subjects)
    full_output_path = os.path.join('data', output_filename)

    if format == 'excel':
        df.to_excel(full_output_path, index=False, engine='openpyxl')
        print(f"Data saved to {full_output_path} as Excel file.")
    elif format == 'parquet':
        df.to_parquet(full_output_path, index=False, engine='auto')  # 'auto' will choose an available engine
        print(f"Data saved to {full_output_path} as Parquet file.")

# Example usage
if __name__=='__main__':
    directory = os.path.join('data')  # Specify the directory containing your files
    filename = find_latest_wanikani_file(directory)  # This will be the full path to the file
    if filename:
        subjects = load_subjects_from_file(os.path.basename(filename))  # Since load_subjects_from_file expects just the filename, not the path
        parsed_subjects = parse_subjects(subjects)
        save_data(parsed_subjects, 'wanikani_subjects.xlsx', 'excel')
        save_data(parsed_subjects, 'wanikani_subjects.parquet', 'parquet')
    else:
        print("Failed to load subjects: No suitable file found.")