# Cache Configuration Update

## Change Made

**Default cache age extended from 7 days to 180 days (~6 months)**

### What This Means

The pipeline will now only fetch fresh data from the WaniKani API if your cached data is **older than 180 days** (approximately 6 months).

### Why This is Better

✅ **Fewer API calls** - Respects WaniKani's rate limits  
✅ **Faster execution** - Uses cached data more often  
✅ **Still fresh enough** - WaniKani core data doesn't change frequently  
✅ **More offline-friendly** - Can work with older cache  

### When Cache is Used

```
Cache Age < 180 days → Use cached data (fast!)
Cache Age > 180 days → Fetch fresh from API
```

### How to Override

If you want fresh data before 180 days:

```bash
# Force fresh data from API
./run_pipeline.sh --fresh

# Or with Python
python wanikani_prefect_flow.py --fresh

# Or custom age
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator" \
    --param max_cache_age_days=30
```

### Files Updated

- ✅ `config.py` - Changed `DEFAULT_MAX_CACHE_AGE_DAYS = 180`
- ✅ `PREFECT_DEPLOYMENT_GUIDE.md` - Updated documentation
- ✅ `README_QUICK_START.md` - Updated quick start guide  
- ✅ `PHASE_2_COMPLETE.md` - Updated summary
- ✅ `run_pipeline.sh` - Already reflected (you edited it!)

### Recommendation

Since WaniKani's radical, kanji, and vocabulary data is relatively static (they don't add new items frequently), **180 days is a good default**. You can always force a refresh when you want:

- After major WaniKani updates
- If you want guaranteed fresh data
- Once or twice a year for peace of mind

### Quick Test

Check current cache age:
```bash
cd wanikani_scripts
ls -lh data/wanikani_subjects_cache_*.json
```

The pipeline will automatically use this cache until it's 180 days old! 🎉
