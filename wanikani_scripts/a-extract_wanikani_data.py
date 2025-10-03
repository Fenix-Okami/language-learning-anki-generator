import requests
import json
from datetime import datetime
import os
import time
from typing import List, Dict, Any
from env import WANIKANI_TOKEN

def fetch_all_subjects(api_token: str, max_retries: int = 3, retry_delay: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches all subjects from the WaniKani API with pagination and retry logic.
    
    Args:
        api_token: WaniKani API token for authentication
        max_retries: Maximum number of retry attempts for failed requests
        retry_delay: Delay in seconds between retry attempts
        
    Returns:
        List of subject dictionaries from the WaniKani API
        
    Raises:
        requests.exceptions.RequestException: If API request fails after retries
        ValueError: If API token is invalid or missing
        json.JSONDecodeError: If API returns invalid JSON
    """
    if not api_token:
        raise ValueError("WaniKani API token is required but was not provided")
    
    try:
        headers = {'Authorization': f'Token token={api_token}'}
        subjects = []
        url = 'https://api.wanikani.com/v2/subjects'
        page_count = 0
        
        print("Starting WaniKani API data extraction...")
        
        while url:
            retry_count = 0
            success = False
            
            # Retry loop for current page
            while retry_count < max_retries and not success:
                try:
                    response = requests.get(url, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        subjects.extend(data['data'])
                        page_count += 1
                        url = data.get('pages', {}).get('next_url')
                        
                        print(f"✓ Fetched page {page_count} ({len(subjects)} subjects total)")
                        success = True
                        
                    elif response.status_code == 401:
                        raise ValueError("Authentication failed: Invalid API token")
                    elif response.status_code == 429:
                        print(f"⚠ Rate limit hit. Waiting {retry_delay * 2} seconds...")
                        time.sleep(retry_delay * 2)
                        retry_count += 1
                    else:
                        print(f"⚠ HTTP {response.status_code}: {response.text}")
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"  Retrying in {retry_delay} seconds... ({retry_count}/{max_retries})")
                            time.sleep(retry_delay)
                        
                except requests.exceptions.Timeout:
                    print("⚠ Request timed out")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"  Retrying in {retry_delay} seconds... ({retry_count}/{max_retries})")
                        time.sleep(retry_delay)
                        
                except requests.exceptions.ConnectionError as e:
                    print(f"⚠ Connection error: {e}")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"  Retrying in {retry_delay} seconds... ({retry_count}/{max_retries})")
                        time.sleep(retry_delay)
                        
                except json.JSONDecodeError as e:
                    print(f"✗ Invalid JSON response: {e}")
                    raise
            
            if not success:
                raise requests.exceptions.RequestException(
                    f"Failed to fetch data after {max_retries} retries"
                )
        
        print(f"✓ Successfully fetched {len(subjects)} subjects from {page_count} pages")
        return subjects
        
    except ValueError as e:
        print(f"✗ Validation error: {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"✗ API request failed: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error during data extraction: {e}")
        raise

def cache_data(subjects: List[Dict[str, Any]], directory: str = 'data', 
               base_filename: str = 'wanikani_subjects_cache') -> str:
    """
    Caches the fetched subjects data to a JSON file with a timestamp.
    
    Args:
        subjects: List of subject dictionaries to cache
        directory: Directory to save the cache file (default: 'data')
        base_filename: Base filename for the cache (default: 'wanikani_subjects_cache')
        
    Returns:
        Full path to the saved cache file
        
    Raises:
        ValueError: If subjects list is empty
        IOError: If there's an error writing the file
    """
    try:
        if not subjects:
            raise ValueError("Cannot cache empty subjects list")
        
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{base_filename}_{today}.json"
        full_path = os.path.join(directory, filename)
        
        # Write the data
        with open(full_path, 'w', encoding='utf-8') as file:
            json.dump(subjects, file, ensure_ascii=False, indent=4)
        
        # Get file size for logging
        file_size_mb = os.path.getsize(full_path) / (1024 * 1024)
        
        print(f"✓ Data cached to {full_path} ({file_size_mb:.2f} MB, {len(subjects)} subjects)")
        return full_path
        
    except ValueError as e:
        print(f"✗ Validation error: {e}")
        raise
    except IOError as e:
        print(f"✗ Error writing cache file: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error caching data: {e}")
        raise

# Main execution
if __name__ == '__main__':
    try:
        print("=" * 60)
        print("WaniKani Data Extraction")
        print("=" * 60)
        
        # Fetch all subjects from the API
        subjects = fetch_all_subjects(WANIKANI_TOKEN)
        
        # Cache the fetched data
        cache_path = cache_data(subjects)
        
        print("\n" + "=" * 60)
        print("✓ Extraction completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Extraction failed: {e}")
        print("=" * 60)
        exit(1)

