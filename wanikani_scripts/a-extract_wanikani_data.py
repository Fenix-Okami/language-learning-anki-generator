import requests
import json
from datetime import datetime
import os  # Added for path manipulation and directory creation
from env import WANIKANI_TOKEN

def fetch_all_subjects(api_token):
    """
    Fetches all subjects from the Wanikani API and returns them as a list.
    """
    headers = {'Authorization': f'Token token={api_token}'}
    subjects = []  # List to accumulate subjects
    url = f'https://api.wanikani.com/v2/subjects'  # Initial URL
    
    while url:  # Loop until there are no more pages
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            subjects.extend(data['data'])  # Add the subjects from the current page
            url = data['pages']['next_url']  # Get the URL for the next page
        else:
            print(f"Failed to fetch data: {response.status_code}")
            break  # Exit loop if there's an error
    
    return subjects

def cache_data(subjects, directory='data', base_filename='wanikani_subjects_cache'):
    """
    Caches the fetched subjects data to a JSON file in a specified directory,
    including the current date in the filename.
    """
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{base_filename}_{today}.json"
    full_path = os.path.join(directory, filename)  # Construct the full file path
    
    with open(full_path, 'w', encoding='utf-8') as file:
        json.dump(subjects, file, ensure_ascii=False, indent=4)
    
    print(f"Data cached to {full_path}")

# Main script
if __name__=='__main__':
    subjects = fetch_all_subjects(WANIKANI_TOKEN)  # Fetch all subjects
    cache_data(subjects)  # Cache the fetched data

