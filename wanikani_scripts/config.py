"""
Configuration module for WaniKani Anki Generator Pipeline.

This module centralizes all configuration constants and environment variables
used throughout the pipeline.
"""

import os
from pathlib import Path
from typing import Optional

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent
WANIKANI_SCRIPTS_DIR = Path(__file__).parent
DATA_DIR = WANIKANI_SCRIPTS_DIR / 'data'
ANKI_DECKS_DIR = WANIKANI_SCRIPTS_DIR / 'ankidecks'

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
ANKI_DECKS_DIR.mkdir(exist_ok=True)

# File naming patterns
CACHE_FILE_PATTERN = 'wanikani_subjects_cache*.json'
CACHE_FILE_BASE = 'wanikani_subjects_cache'
EXCEL_OUTPUT = 'wanikani_subjects.xlsx'
PARQUET_OUTPUT = 'wanikani_subjects.parquet'

# Database configuration
DATABASE_TABLE_NAME = 'wanikani_subjects'
DATABASE_SCHEMA = 'public'

# API configuration
WANIKANI_API_BASE_URL = 'https://api.wanikani.com/v2'
WANIKANI_API_SUBJECTS_ENDPOINT = f'{WANIKANI_API_BASE_URL}/subjects'
API_TIMEOUT_SECONDS = 30
API_MAX_RETRIES = 3
API_RETRY_DELAY_SECONDS = 5

# Cache configuration
DEFAULT_MAX_CACHE_AGE_DAYS = 7

# Anki deck names
ANKI_DECK_NAMES = {
    'radical': 'WaniKani Japanese::Radicals',
    'kanji': 'WaniKani Japanese::Kanji',
    'vocabulary': 'WaniKani Japanese::Vocabulary',
}

ANKI_DECK_FILES = {
    'radical': 'WaniKani_Radical_Deck.apkg',
    'kanji': 'WaniKani_Kanji_Deck.apkg',
    'vocabulary': 'WaniKani_Vocabulary_Deck.apkg',
    'complete': 'WaniKani_Complete_Deck.apkg',
}

# Database view names
DATABASE_VIEWS = {
    'radicals': 'wanikani_radicals',
    'kanji': 'wanikani_kanji',
    'vocabulary': 'wanikani_vocab',
}

# Anki card styling colors
ANKI_COLORS = {
    'radical': '#4193F1',
    'kanji': '#EB417D',
    'vocabulary': '#9F5FBF',
    'background': '#202020',
    'text': '#969696',
    'white': '#FFFFFF',
}

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Environment-specific settings
def get_api_token() -> Optional[str]:
    """Get WaniKani API token from environment or env.py."""
    token = os.getenv('WANIKANI_TOKEN')
    if not token:
        try:
            from env import WANIKANI_TOKEN
            token = WANIKANI_TOKEN
        except ImportError:
            pass
    return token


def get_database_url() -> Optional[str]:
    """Get database URL from environment or env.py."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        try:
            from env import DATABASE_URL
            db_url = DATABASE_URL
        except ImportError:
            pass
    return db_url


# Path helper functions
def get_cache_filepath(filename: str) -> Path:
    """Get full path for cache file."""
    return DATA_DIR / filename


def get_excel_filepath() -> Path:
    """Get full path for Excel output."""
    return DATA_DIR / EXCEL_OUTPUT


def get_parquet_filepath() -> Path:
    """Get full path for Parquet output."""
    return DATA_DIR / PARQUET_OUTPUT


def get_anki_deck_filepath(deck_type: str) -> Path:
    """
    Get full path for Anki deck file.
    
    Args:
        deck_type: Type of deck ('radical', 'kanji', 'vocabulary', 'complete')
        
    Returns:
        Path to the deck file
    """
    if deck_type not in ANKI_DECK_FILES:
        raise ValueError(f"Unknown deck type: {deck_type}")
    return ANKI_DECKS_DIR / ANKI_DECK_FILES[deck_type]
