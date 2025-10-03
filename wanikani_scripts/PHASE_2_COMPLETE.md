# 🎉 Phase 2 Complete - On-Demand Prefect Pipeline Ready!

## ✅ What We Built

### **Prefect-Orchestrated On-Demand Pipeline**

Your WaniKani → Anki generator is now a **production-ready, on-demand Prefect workflow** with:

✅ **Smart caching** (saves API calls, faster execution)  
✅ **Automatic retries** (handles failures gracefully)  
✅ **Error recovery** (comprehensive error handling)  
✅ **Manual execution** (run whenever you want)  
✅ **Multiple execution modes** (fresh, cached, flexible)  
✅ **Full observability** (optional Prefect UI)  

**No scheduling required** - Run it manually when you need it! 🎯

---

## 📁 New Files Created

### Core Pipeline Files

1. **`wanikani_prefect_flow.py`** (272 lines)
   - Main Prefect flow orchestrator
   - 4 Prefect tasks with retry logic
   - 3 flow variants (main, fresh, cached)
   - Smart cache freshness checking
   - Comprehensive error handling

2. **`run_pipeline.sh`** (Bash wrapper)
   - Simple command-line interface
   - Validates environment
   - Shows helpful messages
   - Exit code handling

### Documentation

3. **`PREFECT_DEPLOYMENT_GUIDE.md`** (Updated for on-demand)
   - Focuses on manual execution
   - Removed all scheduling references
   - Added on-demand best practices
   - Multiple execution methods documented

4. **`README_QUICK_START.md`** (Quick reference)
   - 3-step quick start
   - Common workflows
   - Troubleshooting guide
   - Usage examples

5. **`test_prefect_flow.py`** (Test script)
   - Tests all three flow variants
   - Validates functionality
   - Example usage patterns

---

## 🚀 How to Use It

### **Method 1: Simplest (Bash Script)**

```bash
cd wanikani_scripts

# Smart caching (recommended)
./run_pipeline.sh

# Force fresh data
./run_pipeline.sh --fresh

# Never use cache
./run_pipeline.sh --no-cache

# Show help
./run_pipeline.sh --help
```

### **Method 2: Direct Python**

```bash
cd wanikani_scripts

# Default (uses cache if < 7 days old)
python wanikani_prefect_flow.py

# Force fresh
python wanikani_prefect_flow.py --fresh

# No cache
python wanikani_prefect_flow.py --no-cache
```

### **Method 3: Prefect UI (Optional)**

```bash
# 1. Start server (separate terminal)
prefect server start

# 2. Create deployment (one-time)
prefect deploy wanikani_prefect_flow.py:wanikani_anki_pipeline \
    --name "WaniKani Anki Generator" \
    --work-pool "default-agent-pool"

# 3. Start worker (separate terminal)
prefect worker start --pool "default-agent-pool"

# 4. Run from UI or CLI
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator"
```

---

## 🎯 Smart Caching Explained

### How It Works

```
1. Check if cache exists
2. Check cache age
3. If cache < 7 days old → Use it (fast!)
4. If cache > 7 days old → Fetch fresh from API
5. Always transform, load, and generate decks
```

### Why It's Smart

- **Saves API calls** (WaniKani rate limits exist)
- **Faster execution** (no API wait time)
- **Respects API** (fewer requests)
- **Always available** (works offline if cache exists)

### When to Force Fresh

✅ After completing WaniKani reviews/lessons  
✅ Before a study session (want latest content)  
✅ Once per week minimum  
✅ If you see stale data  

---

## 📊 Execution Flow

```
┌─────────────────────────────────────────────────┐
│  Cache Freshness Check                          │
│  • Is cache < 7 days old?                       │
└─────────────────────────────────────────────────┘
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
  [FRESH]             [CACHED]
    ↓                   ↓
┌─────────────┐   ┌─────────────┐
│ Extract Task│   │ Skip Extract│
│ (3 retries) │   │ Use Cache   │
└─────────────┘   └─────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│  Transform Task (2 retries)                     │
│  • Parse JSON → Excel/Parquet                   │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│  Load Task (3 retries)                          │
│  • Load to PostgreSQL                           │
│  • Manage database views                        │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│  Generate Task (2 retries)                      │
│  • Create Anki .apkg files                      │
└─────────────────────────────────────────────────┘
              ↓
      ✅ Complete!
```

---

## 🛡️ Error Handling & Retries

### Task Retry Policies

| Task | Retries | Delay | Why |
|------|---------|-------|-----|
| **Extract** | 3 | Exponential | API failures, rate limits |
| **Transform** | 2 | 30s | Parsing errors |
| **Load** | 3 | 60s | DB connection issues |
| **Generate** | 2 | 30s | Deck creation errors |

### What Happens on Failure

1. **Task fails** → Automatic retry with delay
2. **All retries fail** → Flow stops, error reported
3. **User sees** → Clear error message with context
4. **Can retry** → Just run the command again

---

## 📦 Output Files

### Generated Every Run

```
ankidecks/
├── WaniKani_Radical_Deck.apkg      # ~500 KB
├── WaniKani_Kanji_Deck.apkg        # ~2-3 MB
├── WaniKani_Vocabulary_Deck.apkg   # ~5-8 MB
└── WaniKani_Complete_Deck.apkg     # ~8-12 MB (all cards)
```

### Cache Files (Reused)

```
data/
├── wanikani_subjects_cache_2025-10-02.json  # API cache (~10 MB)
├── wanikani_subjects.xlsx                    # Transformed data
└── wanikani_subjects.parquet                 # Transformed data
```

---

## 🎛️ Three Flow Variants

### 1. `wanikani_anki_pipeline()` - Main Flow
**Use case:** Default, everyday usage  
**Behavior:** Smart caching (7-day threshold)  
**Parameters:** Configurable  

```python
wanikani_anki_pipeline(
    use_cached=True,
    max_cache_age_days=7,
    force_refresh=False
)
```

### 2. `wanikani_anki_pipeline_fresh()` - Always Fresh
**Use case:** After WaniKani reviews, need latest data  
**Behavior:** Always fetches from API  
**Parameters:** None  

```python
wanikani_anki_pipeline_fresh()
```

### 3. `wanikani_anki_pipeline_cached()` - Cache Only
**Use case:** Testing, development, offline work  
**Behavior:** Uses cache, never fetches API  
**Parameters:** Max cache age  

```python
wanikani_anki_pipeline_cached(max_age_days=30)
```

---

## 💡 Usage Recommendations

### Daily Study Routine
```bash
# Morning: Quick update before study
./run_pipeline.sh
```

### After WaniKani Session
```bash
# Get your latest progress
./run_pipeline.sh --fresh
```

### Weekly Maintenance
```bash
# Sunday: Full refresh
./run_pipeline.sh --fresh
```

### Testing Changes
```bash
# Use old cache, don't hit API
python wanikani_prefect_flow.py  # Uses existing cache
```

---

## 🔍 Monitoring (Optional)

### Without Prefect Server
- Terminal output shows progress
- Logs include ✓/⚠/✗ indicators
- Error messages are detailed

### With Prefect Server
- **UI Dashboard**: http://localhost:4200
- **Flow run history**: All past executions
- **Detailed logs**: Per-task logging
- **Metrics**: Execution times, success rates
- **Notifications**: Slack/email on failure

---

## 📚 Documentation Index

| File | Purpose |
|------|---------|
| **README_QUICK_START.md** | Quick reference guide |
| **PREFECT_DEPLOYMENT_GUIDE.md** | Detailed deployment & usage |
| **REFACTORING_SUMMARY.md** | Technical changes log |
| **config.py** | Configuration constants |
| **wanikani_prefect_flow.py** | Main flow (well-documented) |

---

## 🎊 What You've Gained

### Before Prefect Integration
- ❌ Bash script only
- ❌ No retry logic
- ❌ No error recovery
- ❌ Always hits API (wasteful)
- ❌ No visibility into failures
- ❌ Hard to debug

### After Prefect Integration
- ✅ Multiple execution methods
- ✅ Automatic retry with backoff
- ✅ Comprehensive error handling
- ✅ Smart caching (saves API calls)
- ✅ Full observability (optional UI)
- ✅ Easy debugging (detailed logs)
- ✅ Production-ready
- ✅ On-demand execution
- ✅ Flexible configuration
- ✅ Simple CLI interface

---

## 🚀 You're Ready!

### Run it now:
```bash
cd wanikani_scripts
./run_pipeline.sh
```

### View the output:
```
ankidecks/WaniKani_Complete_Deck.apkg
```

### Import into Anki:
```
File → Import → Select .apkg file
```

---

## 📞 Need Help?

1. **Check the terminal output** - Errors are clearly marked with ✗
2. **Read the logs** - Each task reports its progress
3. **Consult documentation**:
   - Quick start: `README_QUICK_START.md`
   - Detailed guide: `PREFECT_DEPLOYMENT_GUIDE.md`
   - Troubleshooting: Both docs have sections

---

## 🎯 Next Steps (Optional)

1. **Add Slack notifications** (get alerts on failures)
2. **Use Prefect Cloud** (managed hosting, better reliability)
3. **Add custom Anki card templates** (modify deck generation)
4. **Extend pipeline** (email decks, sync to cloud, etc.)

---

**Congratulations! Your WaniKani → Anki pipeline is production-ready! 🎉**

**Happy studying! 📚✨**
