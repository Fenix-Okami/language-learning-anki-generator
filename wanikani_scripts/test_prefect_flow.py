#!/usr/bin/env python3
"""
Test script for WaniKani Prefect Flow

This script tests the Prefect flow integration without hitting the API.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from config import (
            get_api_token,
            get_database_url,
            DATA_DIR,
            ANKI_DECKS_DIR
        )
        print("  ✓ config.py imported successfully")
    except Exception as e:
        print(f"  ✗ Failed to import config: {e}")
        return False
    
    try:
        from wanikani_prefect_flow import (
            check_cache_freshness_task,
            wanikani_anki_pipeline,
        )
        print("  ✓ wanikani_prefect_flow.py imported successfully")
    except Exception as e:
        print(f"  ✗ Failed to import flow: {e}")
        return False
    
    return True


def test_configuration():
    """Test that configuration is accessible."""
    print("\nTesting configuration...")
    
    from config import (
        get_api_token,
        get_database_url,
        DATA_DIR,
        ANKI_DECKS_DIR
    )
    
    api_token = get_api_token()
    db_url = get_database_url()
    
    if api_token:
        print(f"  ✓ WaniKani API token configured (length: {len(api_token)})")
    else:
        print("  ⚠ WaniKani API token NOT configured")
        print("    Set WANIKANI_TOKEN environment variable or add to env.py")
    
    if db_url:
        print(f"  ✓ Database URL configured")
    else:
        print("  ⚠ Database URL NOT configured")
        print("    Set DATABASE_URL environment variable or add to env.py")
    
    print(f"  ✓ Data directory: {DATA_DIR}")
    print(f"  ✓ Anki decks directory: {ANKI_DECKS_DIR}")
    
    return bool(api_token and db_url)


def test_cache_check():
    """Test cache freshness checking."""
    print("\nTesting cache freshness check...")
    
    try:
        from wanikani_prefect_flow import check_cache_freshness_task
        
        is_fresh, filepath = check_cache_freshness_task(max_age_days=180)
        
        if is_fresh and filepath:
            print(f"  ✓ Found fresh cache: {filepath}")
        elif filepath:
            print(f"  ⚠ Cache exists but is stale: {filepath}")
        else:
            print("  ℹ No cache files found (expected for first run)")
        
        return True
    except Exception as e:
        print(f"  ✗ Cache check failed: {e}")
        return False


def test_task_definitions():
    """Test that all tasks are properly defined."""
    print("\nTesting task definitions...")
    
    try:
        from wanikani_prefect_flow import (
            check_cache_freshness_task,
            extract_wanikani_data_task,
            transform_data_task,
            load_to_database_task,
            generate_anki_decks_task,
        )
        
        # Check if tasks have Prefect metadata
        tasks = [
            ("Check Cache Freshness", check_cache_freshness_task),
            ("Extract Data", extract_wanikani_data_task),
            ("Transform Data", transform_data_task),
            ("Load to Database", load_to_database_task),
            ("Generate Anki Decks", generate_anki_decks_task),
        ]
        
        for name, task in tasks:
            if hasattr(task, 'task_key'):
                print(f"  ✓ {name} task properly defined")
            else:
                print(f"  ⚠ {name} may not be a proper Prefect task")
        
        return True
    except Exception as e:
        print(f"  ✗ Task definition test failed: {e}")
        return False


def test_flow_definition():
    """Test that the main flow is properly defined."""
    print("\nTesting flow definition...")
    
    try:
        from wanikani_prefect_flow import (
            wanikani_anki_pipeline,
            wanikani_anki_pipeline_fresh,
            wanikani_anki_pipeline_cached,
        )
        
        flows = [
            ("Main Pipeline", wanikani_anki_pipeline),
            ("Fresh Data Pipeline", wanikani_anki_pipeline_fresh),
            ("Cached Data Pipeline", wanikani_anki_pipeline_cached),
        ]
        
        for name, flow in flows:
            if hasattr(flow, 'flow_name'):
                print(f"  ✓ {name} flow properly defined")
            else:
                print(f"  ⚠ {name} may not be a proper Prefect flow")
        
        return True
    except Exception as e:
        print(f"  ✗ Flow definition test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("WaniKani Prefect Flow - Integration Test")
    print("=" * 70)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Cache Check Test", test_cache_check),
        ("Task Definition Test", test_task_definitions),
        ("Flow Definition Test", test_flow_definition),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8} - {test_name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Flow is ready to use.")
        return 0
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
