"""
Prefect Flow for WaniKani → Anki Deck Generation Pipeline

This is a PREVIEW/TEMPLATE showing how the refactored scripts will be
converted into a Prefect workflow.

DO NOT RUN THIS YET - It's a planning document for Phase 2.
"""

from prefect import flow, task
from prefect.blocks.notifications import SlackWebhook
from datetime import datetime, timedelta
from pathlib import Path
import glob

# These will be the refactored functions from our scripts
# from a_extract_wanikani_data import fetch_all_subjects, cache_data
# from b_transform_wanikani_data import load_subjects_from_file, parse_subjects, save_data
# from c_load_wanikani_data import create_database_engine, manage_views, load_excel_to_database
# from d_generate_wanikani_anki_deck import generate_all_decks
from config import (
    get_api_token,
    get_database_url,
    DATA_DIR,
    CACHE_FILE_PATTERN,
    DEFAULT_MAX_CACHE_AGE_DAYS
)


@task(name="Check Cache Freshness", retries=0)
def check_cache_freshness(max_age_days: int = DEFAULT_MAX_CACHE_AGE_DAYS) -> tuple[bool, str | None]:
    """
    Check if a fresh cache file exists.
    
    Returns:
        Tuple of (is_fresh, filepath)
    """
    pattern = str(DATA_DIR / CACHE_FILE_PATTERN)
    cache_files = glob.glob(pattern)
    
    if not cache_files:
        return False, None
    
    # Get the most recent cache file
    latest_file = max(cache_files, key=lambda f: Path(f).stat().st_mtime)
    file_age = datetime.now() - datetime.fromtimestamp(Path(latest_file).stat().st_mtime)
    
    is_fresh = file_age.days < max_age_days
    
    if is_fresh:
        print(f"✓ Found fresh cache ({file_age.days} days old): {latest_file}")
    else:
        print(f"⚠ Cache is stale ({file_age.days} days old): {latest_file}")
    
    return is_fresh, latest_file if is_fresh else None


@task(name="Extract from WaniKani API", retries=3, retry_delay_seconds=60)
def extract_wanikani_data_task(api_token: str) -> str:
    """
    Fetch data from WaniKani API and cache it.
    
    Returns:
        Path to cached JSON file
    """
    # from a_extract_wanikani_data import fetch_all_subjects, cache_data
    
    print("Fetching data from WaniKani API...")
    # subjects = fetch_all_subjects(api_token)
    # cache_path = cache_data(subjects)
    # return cache_path
    
    # Placeholder for now
    return "data/wanikani_subjects_cache_2025-10-02.json"


@task(name="Transform JSON Data", retries=2)
def transform_data_task(json_filepath: str) -> tuple[str, str]:
    """
    Transform JSON to Excel and Parquet formats.
    
    Returns:
        Tuple of (excel_path, parquet_path)
    """
    # from b_transform_wanikani_data import load_subjects_from_file, parse_subjects, save_data
    
    print(f"Transforming data from {json_filepath}...")
    # subjects = load_subjects_from_file(json_filepath)
    # parsed_subjects = parse_subjects(subjects)
    # save_data(parsed_subjects, 'wanikani_subjects.xlsx', 'excel')
    # save_data(parsed_subjects, 'wanikani_subjects.parquet', 'parquet')
    
    # return (
    #     str(DATA_DIR / 'wanikani_subjects.xlsx'),
    #     str(DATA_DIR / 'wanikani_subjects.parquet')
    # )
    
    # Placeholder for now
    return ("data/wanikani_subjects.xlsx", "data/wanikani_subjects.parquet")


@task(name="Load to Database", retries=3, retry_delay_seconds=30)
def load_to_database_task(excel_path: str, database_url: str) -> int:
    """
    Load data from Excel to PostgreSQL database.
    
    Returns:
        Number of rows loaded
    """
    # from c_load_wanikani_data import create_database_engine, manage_views, load_excel_to_database
    # from wanikani_views import views
    
    print(f"Loading {excel_path} to database...")
    # engine = create_database_engine(database_url)
    # manage_views(engine, views, action='drop')
    # row_count = load_excel_to_database(excel_path, engine)
    # manage_views(engine, views, action='create')
    # return row_count
    
    # Placeholder for now
    return 9292


@task(name="Generate Anki Decks", retries=2)
def generate_anki_decks_task(database_url: str) -> dict[str, str]:
    """
    Generate Anki .apkg deck files from database.
    
    Returns:
        Dictionary mapping deck type to filepath
    """
    # from d_generate_wanikani_anki_deck import create_database_engine, generate_all_decks
    
    print("Generating Anki decks...")
    # engine = create_database_engine(database_url)
    # deck_files = generate_all_decks(engine)
    # return deck_files
    
    # Placeholder for now
    return {
        'radical': 'ankidecks/WaniKani_Radical_Deck.apkg',
        'kanji': 'ankidecks/WaniKani_Kanji_Deck.apkg',
        'vocabulary': 'ankidecks/WaniKani_Vocabulary_Deck.apkg',
        'complete': 'ankidecks/WaniKani_Complete_Deck.apkg',
    }


@flow(name="WaniKani → Anki Generator", log_prints=True)
def wanikani_anki_pipeline(
    use_cached: bool = True,
    max_cache_age_days: int = DEFAULT_MAX_CACHE_AGE_DAYS,
    force_refresh: bool = False
) -> dict[str, str]:
    """
    Main Prefect flow for WaniKani → Anki deck generation.
    
    Args:
        use_cached: If True, use local cache if fresh enough (default: True)
        max_cache_age_days: Maximum age in days for cache to be considered fresh (default: 7)
        force_refresh: If True, always fetch fresh data from API (default: False)
        
    Returns:
        Dictionary of generated deck files
        
    Example:
        # Use cached data if available (within 7 days)
        wanikani_anki_pipeline()
        
        # Force fresh fetch from API
        wanikani_anki_pipeline(force_refresh=True)
        
        # Use cache for up to 30 days
        wanikani_anki_pipeline(max_cache_age_days=30)
    """
    print("=" * 60)
    print("🚀 WaniKani → Anki Generation Pipeline")
    print("=" * 60)
    
    # Get credentials
    api_token = get_api_token()
    database_url = get_database_url()
    
    if not api_token:
        raise ValueError("WaniKani API token not configured")
    if not database_url:
        raise ValueError("Database URL not configured")
    
    # Step 1: Determine data source (cached vs fresh)
    json_filepath = None
    
    if use_cached and not force_refresh:
        is_fresh, cached_file = check_cache_freshness(max_cache_age_days)
        if is_fresh and cached_file:
            json_filepath = cached_file
            print("✓ Using cached data")
    
    if not json_filepath:
        print("⚡ Fetching fresh data from WaniKani API")
        json_filepath = extract_wanikani_data_task(api_token)
    
    # Step 2: Transform data
    excel_path, parquet_path = transform_data_task(json_filepath)
    
    # Step 3: Load to database
    row_count = load_to_database_task(excel_path, database_url)
    print(f"✓ Loaded {row_count} rows to database")
    
    # Step 4: Generate Anki decks
    deck_files = generate_anki_decks_task(database_url)
    
    print("\n" + "=" * 60)
    print("✅ Pipeline completed successfully!")
    print("=" * 60)
    print("\n📦 Generated decks:")
    for deck_type, filepath in deck_files.items():
        print(f"  • {deck_type.capitalize()}: {filepath}")
    
    return deck_files


# Deployment configuration (for reference)
"""
To deploy this flow to Prefect:

1. Start Prefect server:
   prefect server start

2. Create a deployment:
   prefect deployment build wanikani_prefect_flow.py:wanikani_anki_pipeline \\
       --name "Daily WaniKani Update" \\
       --cron "0 2 * * *" \\  # Run at 2 AM daily
       --work-queue "default"

3. Apply the deployment:
   prefect deployment apply wanikani_anki_pipeline-deployment.yaml

4. Start a worker:
   prefect worker start --pool "default-agent-pool"

5. Run manually (override parameters):
   prefect deployment run "WaniKani → Anki Generator/Daily WaniKani Update" \\
       --param use_cached=false \\
       --param force_refresh=true
"""


if __name__ == "__main__":
    # For local testing
    result = wanikani_anki_pipeline(
        use_cached=True,
        max_cache_age_days=7,
        force_refresh=False
    )
    print(f"\n✓ Generated {len(result)} deck files")
