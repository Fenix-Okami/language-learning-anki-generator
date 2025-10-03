# Prefect Deployment Guide for WaniKani → Anki Pipeline
## On-Demand Execution (No Scheduling)

This pipeline is designed for **manual, on-demand execution*### **Using Cache (Default Behavior)**

```bash
# ### **1. `wanikani_anki_pipeline()` - Main Flow (Flexible)**
```python
# Smart caching with configurable parameters
wanikani_anki_pipeline(
    use_cached=True,          # Use cache if available
    max_cache_age_days=180,   # Cache valid for 180 days (6 months)
    force_refresh=False        # Don't force API fetch
)he if < 180 days old
python wanikani_prefect_flow.pyy.

---

## Quick Start - Run Locally

### Option 1: Direct Python Execution (Simplest)

```bash
cd wanikani_scripts

# Run with default settings (uses cache if < 7 days old)
python wanikani_prefect_flow.py

# Force fresh data from API
python wanikani_prefect_flow.py --fresh

# Never use cache
python wanikani_prefect_flow.py --no-cache
```

### Option 2: Using Prefect CLI

```bash
cd wanikani_scripts

# Run the flow directly
prefect run wanikani_prefect_flow.py:wanikani_anki_pipeline

# Run with parameters
prefect run wanikani_prefect_flow.py:wanikani_anki_pipeline \
    --param force_refresh=true
```

---

## Setup for On-Demand Execution with Prefect Server

### 1. Start Prefect Server (Optional - for UI and logging)

```bash
# Start Prefect server (in a separate terminal)
prefect server start

# Access UI at: http://localhost:4200

# Or connect to Prefect Cloud
prefect cloud login
```

### 2. Create an On-Demand Deployment (NO SCHEDULE)

```bash
cd wanikani_scripts

# Create deployment WITHOUT a schedule
prefect deploy wanikani_prefect_flow.py:wanikani_anki_pipeline \
    --name "WaniKani Anki Generator" \
    --work-pool "default-agent-pool" \
    --tag "wanikani" \
    --tag "anki" \
    --tag "on-demand"

# Note: NO --cron or --interval flags = manual execution only
```

### 3. Start a Worker (if using Prefect Server)

```bash
# Start a worker to execute flows when triggered
prefect worker start --pool "default-agent-pool"

# Keep this running in a separate terminal or as a background service
```

---

## Running the Pipeline On-Demand

### Method 1: Direct Python (No Server Required)

```bash
cd wanikani_scripts
python wanikani_prefect_flow.py
```

**Pros:**
- ✅ Simplest method
- ✅ No server needed
- ✅ Immediate execution
- ✅ See output in terminal

**Cons:**
- ❌ No UI visibility
- ❌ No historical logs
- ❌ No run tracking

### Method 2: Prefect CLI (No Server Required)

```bash
cd wanikani_scripts
prefect run wanikani_prefect_flow.py:wanikani_anki_pipeline
```

**Pros:**
- ✅ Simple CLI command
- ✅ Can pass parameters
- ✅ No server needed

### Method 3: Trigger via Prefect UI (Server Required)

```bash
# 1. Ensure Prefect server is running
prefect server start

# 2. Open UI: http://localhost:4200

# 3. Navigate to Deployments → "WaniKani Anki Generator"

# 4. Click "Run" → "Quick Run" (or set custom parameters)
```

**Pros:**
- ✅ Visual interface
- ✅ Historical run logs
- ✅ Easy parameter customization
- ✅ Run tracking and metrics
- ✅ Error visibility

**Recommended for:** Regular use with visibility needs

### Method 4: Trigger via Prefect CLI (Server Required)

```bash
# Run the deployment
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator"

# Run with custom parameters
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator" \
    --param force_refresh=true \
    --param max_cache_age_days=30
```

**Pros:**
- ✅ Can be scripted
- ✅ Remote execution
- ✅ Parameter control
- ✅ Tracked in UI

---

## Execution Parameters

### Using Cache (Default Behavior)

```bash
# Uses cache if < 7 days old
python wanikani_prefect_flow.py

# Or via Prefect CLI
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator"
```

### Force Fresh Data from API

```bash
# Direct execution
python wanikani_prefect_flow.py --fresh

# Via deployment
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator" \
    --param force_refresh=true
```

### Custom Cache Age

```bash
# Allow cache up to 30 days old
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator" \
    --param max_cache_age_days=30
```

### Never Use Cache

```bash
# Direct execution
python wanikani_prefect_flow.py --no-cache

# Via deployment
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator" \
    --param use_cached=false
```

---

## Flow Variants

The pipeline includes three flow variants for different use cases:

### 1. `wanikani_anki_pipeline()` - Main Flow (Flexible)
```python
# Smart caching with configurable parameters
wanikani_anki_pipeline(
    use_cached=True,          # Use cache if available
    max_cache_age_days=7,     # Cache valid for 7 days
    force_refresh=False        # Don't force API fetch
)
```
**Use when:** You want flexibility and smart caching

### 2. `wanikani_anki_pipeline_fresh()` - Always Fresh
```python
# Always fetch from API, ignore cache
wanikani_anki_pipeline_fresh()
```
**Use when:** You need guaranteed fresh data (e.g., after WaniKani reviews)

### 3. `wanikani_anki_pipeline_cached()` - Cache Only
```python
# Use existing cache, never fetch from API
wanikani_anki_pipeline_cached(max_age_days=30)
```
**Use when:** Testing, development, or working offline

## Configuration

### Environment Variables

Set these in your environment or `.env` file:

```bash
# Required
export WANIKANI_TOKEN="your-api-token-here"
export DATABASE_URL="postgresql://user:password@localhost:5432/wanikani"

# Optional
export LOG_LEVEL="INFO"
export MAX_CACHE_AGE_DAYS="7"
```

### Prefect Blocks (Optional)

Store credentials securely using Prefect Blocks:

```python
from prefect.blocks.system import Secret

# Create secret blocks
Secret(value="your-api-token").save("wanikani-api-token")
Secret(value="postgresql://...").save("wanikani-db-url")
```

Then update `config.py` to use blocks:

```python
from prefect.blocks.system import Secret

def get_api_token():
    try:
        return Secret.load("wanikani-api-token").get()
    except:
        return os.getenv('WANIKANI_TOKEN')
```

## Monitoring

### View Flow Runs

```bash
# Open Prefect UI
prefect server start

# Navigate to: http://localhost:4200
```

### Check Logs

```bash
# View recent flow runs
prefect flow-run ls

# Get specific flow run logs
prefect flow-run logs <flow-run-id>
```

## Notifications (Optional)

### Setup Slack Notifications

```python
from prefect.blocks.notifications import SlackWebhook

# Create Slack webhook block
slack = SlackWebhook(url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
slack.save("wanikani-notifications")
```

Add to your flow:

```python
from prefect.blocks.notifications import SlackWebhook

@flow(on_failure=[SlackWebhook.load("wanikani-notifications")])
def wanikani_anki_pipeline(...):
    ...
```

### Setup Email Notifications

```python
from prefect.blocks.notifications import EmailServerCredentials

# Configure email
email = EmailServerCredentials(
    username="your-email@gmail.com",
    password="your-app-password",
    smtp_server="smtp.gmail.com",
    smtp_port=587
)
email.save("wanikani-email")
```

## Troubleshooting

### Flow Fails to Start

1. Check credentials are configured:
   ```bash
   python -c "from config import get_api_token, get_database_url; print(bool(get_api_token()), bool(get_database_url()))"
   ```

2. Verify database connection:
   ```bash
   python -c "from c_load_wanikani_data import create_database_engine; from config import get_database_url; create_database_engine(get_database_url())"
   ```

### Worker Not Picking Up Runs

1. Ensure worker is running in same work pool:
   ```bash
   prefect worker start --pool "default-agent-pool"
   ```

2. Check deployment work pool matches:
   ```bash
   prefect deployment inspect "WaniKani → Anki Generator/Daily WaniKani Update"
   ```

### API Rate Limiting

The flow includes automatic retry logic with backoff. If you hit rate limits:

1. Increase cache age: `max_cache_age_days=30`
2. Use cached data more: `use_cached=True`
3. Run less frequently (adjust cron schedule)

## Advanced Usage

### Run Specific Tasks Only

You can import and run individual tasks:

```python
from wanikani_prefect_flow import transform_data_task

# Run just transformation
excel, parquet = transform_data_task("data/wanikani_subjects_cache_2025-10-02.json")
```

### Chain with Other Flows

```python
from prefect import flow
from wanikani_prefect_flow import wanikani_anki_pipeline

@flow
def weekly_study_prep():
    # Generate fresh decks
    decks = wanikani_anki_pipeline(force_refresh=True)
    
    # Additional processing...
    # - Email decks to user
    # - Sync to cloud storage
    # - Generate study statistics
    
    return decks
```

### Parallel Execution

The tasks are already set up for parallel execution where possible. Prefect will automatically parallelize independent tasks.

## Best Practices for On-Demand Usage

### 1. Smart Caching Strategy
- **Default mode**: Use cached data if < 7 days old (saves API calls)
- **After study session**: Run with `force_refresh=true` to get latest progress
- **Offline work**: Use cached mode with longer age tolerance

### 2. When to Force Refresh
✅ After completing WaniKani reviews/lessons  
✅ Before a study session (to get latest content)  
✅ If you notice stale data  
✅ Once per week minimum (to stay current)  

### 3. Credential Management
- ✅ **Recommended**: Store in Prefect Blocks (if using server)
- ✅ **Alternative**: Use environment variables
- ❌ **Never**: Hard-code in scripts

### 4. Error Handling
The pipeline has built-in retry logic:
- **API failures**: 3 retries with exponential backoff
- **Transform errors**: 2 retries with 30s delay
- **Database errors**: 3 retries with 60s delay
- **Deck generation**: 2 retries with 30s delay

### 5. Monitoring (if using Prefect Server)
- View execution history in UI (http://localhost:4200)
- Check logs for any warnings
- Monitor API rate limit usage
- Track deck generation sizes

### 6. Performance Tips
- Use cached mode for quick iterations during testing
- Force refresh when you actually need updated data
- Consider cache age based on your study frequency:
  - Study daily → 7 day cache
  - Study weekly → 14-30 day cache
  - Study monthly → 30+ day cache

---

## Example On-Demand Workflows

### Workflow 1: Daily Study Routine
```bash
# Morning: Get fresh data before study
cd wanikani_scripts
python wanikani_prefect_flow.py --fresh

# Import decks into Anki
# Complete study session
```

### Workflow 2: Occasional Updates
```bash
# Use cached data (faster, API-friendly)
python wanikani_prefect_flow.py

# Force refresh only once a week
python wanikani_prefect_flow.py --fresh  # Weekly
```

### Workflow 3: Testing/Development
```bash
# Use cached data, never hit API
python wanikani_prefect_flow.py --no-cache

# Or extend cache tolerance
python wanikani_prefect_flow.py  # Uses 30+ day old cache if available
```

---

## Quick Reference

### Common Commands

```bash
# Standard run (smart caching)
python wanikani_prefect_flow.py

# Force fresh from API
python wanikani_prefect_flow.py --fresh

# Never use cache
python wanikani_prefect_flow.py --no-cache

# Via Prefect CLI (with server)
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator"

# With custom parameters
prefect deployment run "WaniKani → Anki Generator/WaniKani Anki Generator" \
    --param force_refresh=true
```

### Output Locations

```
wanikani_scripts/
├── data/
│   ├── wanikani_subjects_cache_*.json  # API cache
│   ├── wanikani_subjects.xlsx          # Transformed data
│   └── wanikani_subjects.parquet       # Transformed data
└── ankidecks/
    ├── WaniKani_Radical_Deck.apkg      # Radical cards
    ├── WaniKani_Kanji_Deck.apkg        # Kanji cards
    ├── WaniKani_Vocabulary_Deck.apkg   # Vocabulary cards
    └── WaniKani_Complete_Deck.apkg     # All cards bundled
```
