# WaniKani → Anki Generator - Quick Start

Generate Anki flashcard decks from your WaniKani data with a single command.

---

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies

```bash
cd wanikani_scripts
pip install -r requirements.txt
```

### 2. Configure Credentials

Create `env.py` in the `wanikani_scripts/` directory:

```python
# env.py
WANIKANI_TOKEN = "your-wanikani-api-token"
DATABASE_URL = "postgresql://user:password@localhost:5432/wanikani"
```

**Get your WaniKani API token:** https://www.wanikani.com/settings/personal_access_tokens

### 3. Run the Pipeline

```bash
# Run with smart caching (recommended)
python wanikani_prefect_flow.py

# Or force fresh data from API
python wanikani_prefect_flow.py --fresh
```

**That's it!** 🎉 Your Anki decks are in `ankidecks/`

---

## 📦 What Gets Generated

```
ankidecks/
├── WaniKani_Radical_Deck.apkg      # Radical cards
├── WaniKani_Kanji_Deck.apkg        # Kanji cards  
├── WaniKani_Vocabulary_Deck.apkg   # Vocabulary cards
└── WaniKani_Complete_Deck.apkg     # All cards in one file
```

Import any of these into Anki!

---

## 🎛️ Usage Options

### Default (Smart Caching)
```bash
python wanikani_prefect_flow.py
```
- Uses cached data if < 180 days old (~6 months)
- Fast execution
- API-friendly

### Force Fresh Data
```bash
python wanikani_prefect_flow.py --fresh
```
- Always fetches from WaniKani API
- Gets your latest progress
- Use after completing reviews/lessons

### Never Use Cache
```bash
python wanikani_prefect_flow.py --no-cache
```
- Always fetches fresh, never checks cache
- Guaranteed most recent data

---

## 🔍 How It Works

```
1. Extract  → Fetch data from WaniKani API (or use cache)
2. Transform → Parse and structure data
3. Load      → Store in PostgreSQL database
4. Generate  → Create Anki .apkg deck files
```

The pipeline automatically:
- ✅ Retries on failures
- ✅ Tracks progress
- ✅ Validates data
- ✅ Reports errors clearly

---

## 📊 Advanced: Use Prefect UI (Optional)

For better visibility and monitoring:

```bash
# 1. Start Prefect server (separate terminal)
prefect server start

# 2. Create deployment (one-time setup)
cd wanikani_scripts
prefect deploy wanikani_prefect_flow.py:wanikani_anki_pipeline \
    --name "WaniKani Anki Generator" \
    --work-pool "default-agent-pool"

# 3. Start worker (separate terminal)
prefect worker start --pool "default-agent-pool"

# 4. Access UI
open http://localhost:4200
```

Then run from the UI or CLI:
```bash
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator"
```

**Benefits:**
- 📈 View execution history
- 📋 Check detailed logs
- 🎯 Run with custom parameters via UI
- ⚠️ Get failure notifications

---

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named..."
```bash
pip install -r requirements.txt
```

### "ValueError: WaniKani API token is required"
Check that `env.py` exists with your API token:
```python
WANIKANI_TOKEN = "your-token-here"
```

### "Database connection failed"
Ensure PostgreSQL is running and `DATABASE_URL` is correct in `env.py`

### "No matching wanikani_subjects*.json files found"
First run will fetch from API. This is normal! The cache will be created for future runs.

---

## 📚 Documentation

- **[PREFECT_DEPLOYMENT_GUIDE.md](PREFECT_DEPLOYMENT_GUIDE.md)** - Detailed deployment guide
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Technical changes log
- **[config.py](config.py)** - All configuration constants

---

## 🎯 Common Workflows

### After completing WaniKani reviews:
```bash
cd wanikani_scripts
python wanikani_prefect_flow.py --fresh
# Import WaniKani_Complete_Deck.apkg into Anki
```

### Weekly update routine:
```bash
# Monday morning
python wanikani_prefect_flow.py --fresh
```

### Quick update (uses cache):
```bash
python wanikani_prefect_flow.py
```

---

## ⚙️ Configuration

Edit [`config.py`](config.py) to customize:
- Cache directory locations
- File naming patterns
- API timeouts and retries
- Anki card colors and styling
- Database table names

---

## 🤝 Need Help?

Check the logs in the terminal output - they include helpful status indicators:
- ✓ Success
- ⚠ Warning
- ✗ Error

For detailed documentation, see **[PREFECT_DEPLOYMENT_GUIDE.md](PREFECT_DEPLOYMENT_GUIDE.md)**

---

**Happy studying! 📚✨**
