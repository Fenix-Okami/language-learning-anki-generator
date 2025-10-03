import json
import pandas as pd
import os
import glob
import numpy as np
from typing import List, Dict, Any, Optional

def load_subjects_from_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Loads subjects from a JSON file and returns them as a list of dictionaries.
    
    Args:
        filepath: Full path to the JSON file containing WaniKani subjects data
        
    Returns:
        List of subject dictionaries from the JSON file
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
        IOError: If there's an error reading the file
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Subject file not found: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        if not isinstance(data, list):
            raise ValueError(f"Expected JSON array but got {type(data).__name__}")
            
        print(f"✓ Successfully loaded {len(data)} subjects from {filepath}")
        return data
        
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in {filepath}: {e}")
        raise
    except IOError as e:
        print(f"✗ Error reading file {filepath}: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error loading subjects: {e}")
        raise 

def parse_subjects(subjects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parses a list of subjects, extracting comprehensive information for each.
    
    Args:
        subjects: List of raw subject dictionaries from WaniKani API
        
    Returns:
        List of parsed and normalized subject dictionaries
        
    Raises:
        ValueError: If subjects list is empty or contains invalid data
    """
    if not subjects:
        raise ValueError("Cannot parse empty subjects list")
        
    try:
        parsed_subjects = []
        total = len(subjects)
        
        for idx, subject in enumerate(subjects, 1):
            try:
                parsed_data = parse_subject_data(subject)
                # Convert numpy arrays to lists if present
                for key, value in parsed_data.items():
                    if isinstance(value, np.ndarray):
                        parsed_data[key] = value.tolist()
                parsed_subjects.append(parsed_data)
                
            except Exception as e:
                subject_id = subject.get('id', 'unknown')
                print(f"⚠ Warning: Failed to parse subject {subject_id} ({idx}/{total}): {e}")
                continue
                
        print(f"✓ Successfully parsed {len(parsed_subjects)}/{total} subjects")
        return parsed_subjects
        
    except Exception as e:
        print(f"✗ Error parsing subjects: {e}")
        raise

def parse_subject_data(subject_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses the API response and extracts a comprehensive set of information,
    including separating kanji readings into on'yomi and kun'yomi.
    
    Args:
        subject_data: Raw subject dictionary from WaniKani API
        
    Returns:
        Dictionary with parsed and normalized subject information
        
    Raises:
        KeyError: If required fields are missing from subject_data
    """
    try:
        data = subject_data.get('data', {})
        subject_type = subject_data.get('object')
        
        if not subject_type:
            raise ValueError("Subject missing 'object' type field")
        
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
        
    except KeyError as e:
        subject_id = subject_data.get('id', 'unknown')
        raise KeyError(f"Missing required field in subject {subject_id}: {e}")
    except Exception as e:
        subject_id = subject_data.get('id', 'unknown')
        raise ValueError(f"Error parsing subject {subject_id}: {e}")


def save_to_excel(parsed_subjects: List[Dict[str, Any]], output_filename: str) -> None:
    """
    Saves parsed subjects to an Excel file.
    
    Args:
        parsed_subjects: List of parsed subject dictionaries
        output_filename: Name of the output Excel file
        
    Raises:
        ValueError: If parsed_subjects is empty
        IOError: If there's an error writing the file
    
    Note: This function is deprecated. Use save_data() instead.
    """
    try:
        if not parsed_subjects:
            raise ValueError("Cannot save empty subjects list")
            
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(parsed_subjects)
        
        # Construct the full path using os.path.join for the output file
        full_output_path = os.path.join('data', output_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
        
        # Save the DataFrame to an Excel file
        df.to_excel(full_output_path, index=False, engine='openpyxl')
        print(f"✓ Data saved to {full_output_path}")
        
    except Exception as e:
        print(f"✗ Error saving to Excel: {e}")
        raise

def find_latest_wanikani_file(directory: str) -> Optional[str]:
    """
    Finds the latest file in the specified directory that starts with 'wanikani_subjects' and ends with '.json'.
    Returns the full path of the most recently modified file.
    
    Args:
        directory: Directory path to search for WaniKani subject files
        
    Returns:
        Full path to the latest file, or None if no matching files found
        
    Raises:
        OSError: If there's an error accessing the directory
    """
    try:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
            
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")
            
        pattern = os.path.join(directory, 'wanikani_subjects*.json')
        files = glob.glob(pattern)
        
        if not files:
            print(f"⚠ Warning: No matching wanikani_subjects*.json files found in {directory}")
            return None
            
        # Sort files by modification time and return the most recent
        latest_file = max(files, key=os.path.getmtime)
        print(f"✓ Found latest file: {os.path.basename(latest_file)}")
        return latest_file
        
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"✗ Error: {e}")
        raise
    except Exception as e:
        print(f"✗ Error finding latest file: {e}")
        raise
    
def save_data(parsed_subjects: List[Dict[str, Any]], output_filename: str, format: str = 'excel') -> None:
    """
    Saves parsed subjects to a file in the specified format.
    
    Args:
        parsed_subjects: List of parsed subject dictionaries
        output_filename: Name of the output file
        format: Output format - either 'excel' or 'parquet' (default: 'excel')
        
    Raises:
        ValueError: If parsed_subjects is empty or format is unsupported
        IOError: If there's an error writing the file
    """
    try:
        if not parsed_subjects:
            raise ValueError("Cannot save empty subjects list")
            
        if format not in ['excel', 'parquet']:
            raise ValueError(f"Unsupported format: {format}. Use 'excel' or 'parquet'")
            
        df = pd.DataFrame(parsed_subjects)
        full_output_path = os.path.join('data', output_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)

        if format == 'excel':
            df.to_excel(full_output_path, index=False, engine='openpyxl')
            print(f"✓ Data saved to {full_output_path} as Excel file ({len(df)} rows)")
        elif format == 'parquet':
            df.to_parquet(full_output_path, index=False, engine='auto')
            print(f"✓ Data saved to {full_output_path} as Parquet file ({len(df)} rows)")
            
    except ValueError as e:
        print(f"✗ Validation error: {e}")
        raise
    except Exception as e:
        print(f"✗ Error saving data to {format}: {e}")
        raise

# Main execution
if __name__ == '__main__':
    try:
        print("=" * 60)
        print("WaniKani Data Transformation Pipeline")
        print("=" * 60)
        
        # Find the latest WaniKani subjects file
        directory = os.path.join('data')
        filepath = find_latest_wanikani_file(directory)
        
        if not filepath:
            print("✗ Failed to load subjects: No suitable file found.")
            exit(1)
        
        # Load subjects from the file (now using full path consistently)
        subjects = load_subjects_from_file(filepath)
        
        # Parse the subjects
        print(f"\nParsing {len(subjects)} subjects...")
        parsed_subjects = parse_subjects(subjects)
        
        # Save in multiple formats
        print("\nSaving parsed data...")
        save_data(parsed_subjects, 'wanikani_subjects.xlsx', 'excel')
        save_data(parsed_subjects, 'wanikani_subjects.parquet', 'parquet')
        
        print("\n" + "=" * 60)
        print("✓ Pipeline completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Pipeline failed: {e}")
        print("=" * 60)
        exit(1)