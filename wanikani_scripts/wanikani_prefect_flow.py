"""
Prefect Flow for WaniKani → Anki Deck Generation Pipeline

This flow orchestrates the complete pipeline from data extraction to deck generation,
with conditional execution based on cache freshness.
"""

from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import datetime, timedelta
from pathlib import Path
import glob
import importlib.util
import sys
from typing import Dict, Tuple, Optional

# Import configuration
from config import (
    get_api_token,
    get_database_url,
    DATA_DIR,
    CACHE_FILE_PATTERN,
    DEFAULT_MAX_CACHE_AGE_DAYS,
    get_excel_filepath,
    get_parquet_filepath,
)
from wanikani_views import views

# Helper to import modules with hyphens
def import_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Get current directory
current_dir = Path(__file__).parent

# Import modules
extract_module = import_module_from_path(
    "a_extract_wanikani_data",
    str(current_dir / "a-extract_wanikani_data.py")
)
transform_module = import_module_from_path(
    "b_transform_wanikani_data",
    str(current_dir / "b-transform_wanikani_data.py")
)
load_module = import_module_from_path(
    "c_load_wanikani_data",
    str(current_dir / "c-load_wanikani_data.py")
)
generate_module = import_module_from_path(
    "d_generate_wanikani_anki_deck",
    str(current_dir / "d-generate_wanikani_anki_deck.py")
)

# Extract functions
fetch_all_subjects = extract_module.fetch_all_subjects
cache_data = extract_module.cache_data

load_subjects_from_file = transform_module.load_subjects_from_file
parse_subjects = transform_module.parse_subjects
save_data = transform_module.save_data

create_database_engine = load_module.create_database_engine
manage_views = load_module.manage_views
load_excel_to_database = load_module.load_excel_to_database

generate_all_decks = generate_module.generate_all_decks
create_database_engine_for_deck = generate_module.create_database_engine


@task(
    name="Check Cache Freshness",
    description="Determines if existing cache is fresh enough to use",
    retries=0,
    log_prints=True,
)
def check_cache_freshness_task(max_age_days: int = DEFAULT_MAX_CACHE_AGE_DAYS) -> Tuple[bool, Optional[str]]:
    """
    Check if a fresh cache file exists.
    
    Args:
        max_age_days: Maximum age in days for cache to be considered fresh
        
    Returns:
        Tuple of (is_fresh: bool, filepath: str | None)
    """
    try:
        pattern = str(DATA_DIR / CACHE_FILE_PATTERN)
        cache_files = glob.glob(pattern)
        
        if not cache_files:
            print("No cache files found")
            return False, None
        
        # Get the most recent cache file
        latest_file = max(cache_files, key=lambda f: Path(f).stat().st_mtime)
        file_age = datetime.now() - datetime.fromtimestamp(Path(latest_file).stat().st_mtime)
        
        is_fresh = file_age.days < max_age_days
        
        if is_fresh:
            print(f"✓ Found fresh cache ({file_age.days} days old): {latest_file}")
        else:
            print(f"⚠ Cache is stale ({file_age.days} days old, max: {max_age_days})")
        
        return is_fresh, latest_file if is_fresh else None
        
    except Exception as e:
        print(f"⚠ Error checking cache: {e}")
        return False, None


@task(
    name="Extract from WaniKani API",
    description="Fetch all subjects from WaniKani API and cache locally",
    retries=3,
    retry_delay_seconds=60,
    log_prints=True,
)
def extract_wanikani_data_task(api_token: str) -> str:
    """
    Fetch data from WaniKani API and cache it.
    
    Args:
        api_token: WaniKani API authentication token
        
    Returns:
        Path to cached JSON file
        
    Raises:
        ValueError: If API token is invalid
        requests.exceptions.RequestException: If API request fails
    """
    print("📡 Fetching data from WaniKani API...")
    subjects = fetch_all_subjects(api_token)
    cache_path = cache_data(subjects)
    return cache_path


@task(
    name="Transform JSON Data",
    description="Parse JSON and convert to Excel/Parquet formats",
    retries=2,
    retry_delay_seconds=30,
    log_prints=True,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=24),
)
def transform_data_task(json_filepath: str) -> Tuple[str, str]:
    """
    Transform JSON to Excel and Parquet formats.
    
    Args:
        json_filepath: Path to JSON cache file
        
    Returns:
        Tuple of (excel_path, parquet_path)
        
    Raises:
        FileNotFoundError: If JSON file doesn't exist
        ValueError: If data parsing fails
    """
    print(f"🔄 Transforming data from {json_filepath}...")
    
    # Load and parse subjects
    subjects = load_subjects_from_file(json_filepath)
    parsed_subjects = parse_subjects(subjects)
    
    # Save in both formats
    save_data(parsed_subjects, 'wanikani_subjects.xlsx', 'excel')
    save_data(parsed_subjects, 'wanikani_subjects.parquet', 'parquet')
    
    excel_path = str(get_excel_filepath())
    parquet_path = str(get_parquet_filepath())
    
    return excel_path, parquet_path


@task(
    name="Load to Database",
    description="Load transformed data into PostgreSQL database",
    retries=3,
    retry_delay_seconds=30,
    log_prints=True,
)
def load_to_database_task(excel_path: str, database_url: str) -> int:
    """
    Load data from Excel to PostgreSQL database.
    
    Args:
        excel_path: Path to Excel file
        database_url: PostgreSQL connection URL
        
    Returns:
        Number of rows loaded
        
    Raises:
        FileNotFoundError: If Excel file doesn't exist
        SQLAlchemyError: If database operation fails
    """
    print(f"📥 Loading data from {excel_path} to database...")
    
    # Create database engine
    engine = create_database_engine(database_url)
    
    # Drop existing views
    print("Dropping existing views...")
    manage_views(engine, views, action='drop')
    
    # Load data
    row_count = load_excel_to_database(excel_path, engine)
    
    # Recreate views
    print("Recreating views...")
    manage_views(engine, views, action='create')
    
    return row_count


@task(
    name="Generate Anki Decks",
    description="Generate Anki .apkg deck files from database",
    retries=2,
    retry_delay_seconds=30,
    log_prints=True,
)
def generate_anki_decks_task(database_url: str) -> Dict[str, str]:
    """
    Generate Anki .apkg deck files from database.
    
    Args:
        database_url: PostgreSQL connection URL
        
    Returns:
        Dictionary mapping deck type to filepath
        
    Raises:
        SQLAlchemyError: If database query fails
        IOError: If file writing fails
    """
    print("🎴 Generating Anki decks...")
    
    # Create database engine
    engine = create_database_engine_for_deck(database_url)
    
    # Generate all decks
    deck_files = generate_all_decks(engine)
    
    return deck_files


@flow(
    name="WaniKani → Anki Generator",
    description="Complete pipeline from WaniKani API to Anki deck generation",
    log_prints=True,
)
def wanikani_anki_pipeline(
    use_cached: bool = True,
    max_cache_age_days: int = DEFAULT_MAX_CACHE_AGE_DAYS,
    force_refresh: bool = False,
) -> Dict[str, str]:
    """
    Main Prefect flow for WaniKani → Anki deck generation.
    
    This flow orchestrates the complete pipeline with intelligent caching:
    - Checks if recent cache exists
    - Conditionally fetches fresh data from API
    - Transforms data to Excel/Parquet
    - Loads to PostgreSQL database
    - Generates Anki deck files
    
    Args:
        use_cached: If True, use local cache if fresh enough (default: True)
        max_cache_age_days: Maximum age in days for cache to be fresh (default: 7)
        force_refresh: If True, always fetch fresh data from API (default: False)
        
    Returns:
        Dictionary mapping deck type to generated file path
        
    Raises:
        ValueError: If credentials are missing or invalid
        
    Examples:
        # Use cached data if available (within 7 days)
        >>> wanikani_anki_pipeline()
        
        # Force fresh fetch from API
        >>> wanikani_anki_pipeline(force_refresh=True)
        
        # Use cache for up to 30 days
        >>> wanikani_anki_pipeline(max_cache_age_days=30)
        
        # Never use cache, always fetch fresh
        >>> wanikani_anki_pipeline(use_cached=False)
    """
    print("=" * 70)
    print("🚀 WaniKani → Anki Generation Pipeline")
    print("=" * 70)
    print(f"   Config: use_cached={use_cached}, max_age={max_cache_age_days} days")
    print(f"           force_refresh={force_refresh}")
    print("=" * 70)
    
    # Validate credentials
    api_token = get_api_token()
    database_url = get_database_url()
    
    if not api_token:
        raise ValueError(
            "WaniKani API token not configured. "
            "Set WANIKANI_TOKEN environment variable or add to env.py"
        )
    if not database_url:
        raise ValueError(
            "Database URL not configured. "
            "Set DATABASE_URL environment variable or add to env.py"
        )
    
    # Step 1: Determine data source (cached vs fresh)
    json_filepath = None
    
    if use_cached and not force_refresh:
        print("\n📂 Checking for cached data...")
        is_fresh, cached_file = check_cache_freshness_task(max_cache_age_days)
        
        if is_fresh and cached_file:
            json_filepath = cached_file
            print("✓ Using cached data")
        else:
            print("⚡ Cache miss - will fetch fresh data")
    else:
        if force_refresh:
            print("\n⚡ Force refresh enabled - fetching fresh data")
        else:
            print("\n⚡ Cache disabled - fetching fresh data")
    
    # Step 2: Extract (conditionally)
    if not json_filepath:
        json_filepath = extract_wanikani_data_task(api_token)
    
    # Step 3: Transform
    print("\n" + "-" * 70)
    excel_path, parquet_path = transform_data_task(json_filepath)
    
    # Step 4: Load to database
    print("\n" + "-" * 70)
    row_count = load_to_database_task(excel_path, database_url)
    print(f"✓ Loaded {row_count:,} rows to database")
    
    # Step 5: Generate Anki decks
    print("\n" + "-" * 70)
    deck_files = generate_anki_decks_task(database_url)
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ Pipeline completed successfully!")
    print("=" * 70)
    print("\n📦 Generated Anki Decks:")
    for deck_type, filepath in deck_files.items():
        print(f"   • {deck_type.capitalize():12} → {filepath}")
    print("\n" + "=" * 70)
    
    return deck_files


# Convenience flows for specific use cases
@flow(name="WaniKani → Anki (Fresh Data)")
def wanikani_anki_pipeline_fresh() -> Dict[str, str]:
    """
    Run pipeline with fresh data fetch from WaniKani API.
    Equivalent to: wanikani_anki_pipeline(force_refresh=True)
    """
    return wanikani_anki_pipeline(force_refresh=True)


@flow(name="WaniKani → Anki (Cached)")
def wanikani_anki_pipeline_cached(max_age_days: int = 30) -> Dict[str, str]:
    """
    Run pipeline using cached data (up to specified age).
    Equivalent to: wanikani_anki_pipeline(max_cache_age_days=max_age_days)
    """
    return wanikani_anki_pipeline(max_cache_age_days=max_age_days)


if __name__ == "__main__":
    # For local testing and development
    import sys
    
    # Parse simple command-line arguments
    force_refresh = "--fresh" in sys.argv or "-f" in sys.argv
    no_cache = "--no-cache" in sys.argv
    
    if no_cache:
        result = wanikani_anki_pipeline(use_cached=False)
    elif force_refresh:
        result = wanikani_anki_pipeline(force_refresh=True)
    else:
        result = wanikani_anki_pipeline()
    
    print(f"\n✓ Generated {len(result)} deck files")
