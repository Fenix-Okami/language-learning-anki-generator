"""
Example: Using the WaniKani pipeline as a library in your own scripts.

This shows how to import and use the pipeline programmatically.
"""

from wanikani_prefect_flow import (
    wanikani_anki_pipeline,
    wanikani_anki_pipeline_fresh,
    wanikani_anki_pipeline_cached
)

# Example 1: Basic usage in a script
def update_anki_decks():
    """Simple function to update Anki decks."""
    print("Updating WaniKani Anki decks...")
    deck_files = wanikani_anki_pipeline()
    print(f"Generated {len(deck_files)} decks")
    return deck_files


# Example 2: Force fresh data
def force_refresh_decks():
    """Force fetch fresh data from WaniKani API."""
    print("Forcing fresh data fetch...")
    deck_files = wanikani_anki_pipeline_fresh()
    print(f"Generated fresh decks: {list(deck_files.keys())}")
    return deck_files


# Example 3: Use with custom cache age
def update_with_custom_cache(max_days=14):
    """Update with custom cache age tolerance."""
    print(f"Using cache up to {max_days} days old...")
    deck_files = wanikani_anki_pipeline(
        use_cached=True,
        max_cache_age_days=max_days,
        force_refresh=False
    )
    return deck_files


# Example 4: Integrate with other workflows
def weekly_study_prep():
    """
    Weekly study preparation workflow.
    Combines deck generation with other tasks.
    """
    print("Starting weekly study prep...")
    
    # 1. Generate fresh Anki decks
    print("Step 1: Generating Anki decks...")
    decks = wanikani_anki_pipeline_fresh()
    
    # 2. Your custom processing here
    print("Step 2: Processing decks...")
    for deck_type, filepath in decks.items():
        print(f"  • {deck_type}: {filepath}")
        # Example: Copy to Anki directory, upload to cloud, etc.
    
    # 3. Additional tasks
    print("Step 3: Additional tasks...")
    # Example: Generate study statistics, send notifications, etc.
    
    print("Weekly prep complete!")
    return decks


# Example 5: Conditional execution
def smart_update(force_fresh_if_reviews=False):
    """
    Smart update that chooses fresh vs cached based on context.
    
    Args:
        force_fresh_if_reviews: If True, forces fresh data fetch
    """
    if force_fresh_if_reviews:
        print("Reviews detected - fetching fresh data...")
        return wanikani_anki_pipeline_fresh()
    else:
        print("No reviews - using cached data if available...")
        return wanikani_anki_pipeline()


# Example 6: Error handling
def safe_deck_update():
    """Update decks with error handling."""
    try:
        decks = wanikani_anki_pipeline()
        print("✓ Decks updated successfully!")
        return decks
    except Exception as e:
        print(f"✗ Failed to update decks: {e}")
        # Handle error - send notification, log, etc.
        raise


# Example 7: Use in a larger application
class WaniKaniSyncManager:
    """Example class that manages WaniKani synchronization."""
    
    def __init__(self, cache_days=7):
        self.cache_days = cache_days
        self.last_sync = None
    
    def sync(self, force=False):
        """Sync WaniKani data and generate decks."""
        print(f"Syncing WaniKani data (force={force})...")
        
        if force:
            decks = wanikani_anki_pipeline_fresh()
        else:
            decks = wanikani_anki_pipeline(
                max_cache_age_days=self.cache_days
            )
        
        self.last_sync = decks
        return decks
    
    def get_last_sync_status(self):
        """Get status of last sync."""
        if self.last_sync:
            return f"Last sync generated {len(self.last_sync)} decks"
        return "No sync performed yet"


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("WaniKani Pipeline - Library Usage Examples")
    print("=" * 60)
    
    # Run one of the examples
    print("\nExample 1: Basic update")
    decks = update_anki_decks()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    
    # Uncomment to run other examples:
    # decks = force_refresh_decks()
    # decks = update_with_custom_cache(max_days=30)
    # decks = weekly_study_prep()
    # decks = smart_update(force_fresh_if_reviews=True)
    # decks = safe_deck_update()
    
    # Example with class:
    # manager = WaniKaniSyncManager(cache_days=14)
    # manager.sync(force=False)
    # print(manager.get_last_sync_status())
