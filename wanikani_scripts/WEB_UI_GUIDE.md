# 🌐 Running WaniKani Pipeline from Web UI

This guide shows you how to trigger your pipeline from Prefect's web interface instead of the command line.

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Run the Setup Script

```bash
cd wanikani_scripts
./setup_prefect_server.sh
```

This will:
- Create the work pool
- Create the deployment
- Give you further instructions

### Step 2: Start Two Terminals

**Terminal 1 - Prefect Server:**
```bash
cd wanikani_scripts
./start_prefect_server.sh
```
Keep this running! It hosts the web UI.

**Terminal 2 - Prefect Worker:**
```bash
cd wanikani_scripts
./start_prefect_worker.sh
```
Keep this running! It executes your flows.

### Step 3: Open the Web UI

Open your browser to: **http://localhost:4200**

---

## 🎯 How to Trigger the Pipeline from Web UI

### Method 1: Quick Run (Simple)

1. Open http://localhost:4200
2. Click **"Deployments"** in the left sidebar
3. Find **"WaniKani Anki Generator"**
4. Click the **"Run"** button (▶️)
5. Click **"Quick run"**
6. Done! Watch it execute in real-time

### Method 2: Custom Run (With Parameters)

1. Open http://localhost:4200
2. Click **"Deployments"** in the left sidebar
3. Find **"WaniKani Anki Generator"**
4. Click the **"Run"** button (▶️)
5. Click **"Custom run"**
6. Set parameters:
   ```json
   {
     "use_cached": true,
     "max_cache_age_days": 180,
     "force_refresh": false
   }
   ```
7. Click **"Run"**
8. Watch the execution!

---

## 🎛️ Common Parameter Combinations

### Default (Use Cache if < 180 Days Old)
```json
{
  "use_cached": true,
  "max_cache_age_days": 180,
  "force_refresh": false
}
```

### Force Fresh Data from API
```json
{
  "use_cached": true,
  "max_cache_age_days": 180,
  "force_refresh": true
}
```

### Never Use Cache
```json
{
  "use_cached": false,
  "max_cache_age_days": 180,
  "force_refresh": false
}
```

### Use Cache Up to 1 Year Old
```json
{
  "use_cached": true,
  "max_cache_age_days": 365,
  "force_refresh": false
}
```

---

## 📊 Monitoring Your Flow

### While Running

In the UI, you'll see:
- ✅ **Real-time task progress** (Extract → Transform → Load → Generate)
- ⏱️ **Execution time** for each task
- 📋 **Logs** for each step
- 📊 **Task state** (Running/Completed/Failed)

### After Completion

- 📈 **Flow run history** (all past executions)
- 📋 **Detailed logs** (click any flow run)
- ⚠️ **Error details** (if something failed)
- 📊 **Success/failure metrics**

---

## 🔄 Typical Workflow

### Daily Use:
1. Open http://localhost:4200
2. Go to Deployments → WaniKani Anki Generator
3. Click "Run" → "Quick run"
4. Wait for completion (~1-2 minutes with cache)
5. Find your decks in `ankidecks/`

### After WaniKani Session:
1. Open http://localhost:4200
2. Go to Deployments → WaniKani Anki Generator
3. Click "Run" → "Custom run"
4. Set `force_refresh: true`
5. Click "Run"
6. Import fresh decks into Anki

---

## 🛠️ Management Scripts

We've created helper scripts for you:

### Setup (One-Time)
```bash
./setup_prefect_server.sh
```

### Start Server (Keep Running)
```bash
./start_prefect_server.sh
```

### Start Worker (Keep Running)
```bash
./start_prefect_worker.sh
```

### Stop Everything
Just press `Ctrl+C` in each terminal window.

---

## 💡 Tips & Tricks

### Tip 1: Keep Terminals Open
Both server and worker terminals must stay open for the UI to work.

### Tip 2: Bookmark the UI
Add http://localhost:4200 to your browser bookmarks for quick access.

### Tip 3: Check Worker Status
In the UI: **Work Pools → default-agent-pool** shows if your worker is active.

### Tip 4: View Flow History
**Flow Runs** in the sidebar shows all past executions with logs.

### Tip 5: Use Tags
Your deployment is tagged with `wanikani`, `anki`, and `on-demand` for easy filtering.

---

## 🔍 Troubleshooting

### "No work pools found"
**Fix:** Run `./setup_prefect_server.sh` again

### "Worker not picking up runs"
**Fix:** Make sure `./start_prefect_worker.sh` is running in a terminal

### "Cannot connect to UI"
**Fix:** Make sure `./start_prefect_server.sh` is running in a terminal

### "Flow stuck in 'Scheduled' state"
**Fix:** Check that the worker terminal is still running

### "Connection refused"
**Fix:** Restart the Prefect server:
```bash
# Stop: Ctrl+C in server terminal
# Start: ./start_prefect_server.sh
```

---

## 📱 Alternative: Command Line (No UI Needed)

If you don't want to keep terminals open, you can still use:

```bash
# Simple execution
./run_pipeline.sh

# Force fresh
./run_pipeline.sh --fresh

# Or direct Python
python wanikani_prefect_flow.py
```

---

## 🎯 Recommended Setup

### For Regular Use (Best Experience):

**Option A: Use tmux/screen** (Keeps terminals running in background)
```bash
# Terminal 1
tmux new -s prefect-server
./start_prefect_server.sh

# Terminal 2  
tmux new -s prefect-worker
./start_prefect_worker.sh

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t prefect-server
```

**Option B: Use systemd services** (Linux - runs as background service)
See `ADVANCED_DEPLOYMENT.md` for details (if you want to create this)

**Option C: Just use the bash script** (Simplest)
```bash
./run_pipeline.sh
```

---

## 🌟 Benefits of Web UI

✅ **Visual feedback** - See exactly what's happening  
✅ **Parameter control** - Easy to adjust settings  
✅ **History** - View all past runs  
✅ **Logs** - Detailed execution logs  
✅ **Monitoring** - Real-time task progress  
✅ **Error visibility** - Clear error messages  
✅ **No command line** - Click to run  

---

## 🎊 You're Ready!

1. Run: `./setup_prefect_server.sh` (one-time)
2. Keep running: `./start_prefect_server.sh` (Terminal 1)
3. Keep running: `./start_prefect_worker.sh` (Terminal 2)
4. Open: http://localhost:4200
5. Click: Deployments → WaniKani Anki Generator → Run
6. Done! 🎉

---

## 📞 Need Help?

- **Setup issues**: Run `./setup_prefect_server.sh` again
- **Server issues**: Check Terminal 1 for errors
- **Worker issues**: Check Terminal 2 for errors
- **UI issues**: Try restarting both server and worker

**Happy deck generating from the web UI! 🌐✨**
