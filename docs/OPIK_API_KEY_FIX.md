# 🔧 OPIK API Key Issue - Diagnosis & Fix

## The Issue

```
OPIK_INIT: Configuration warning (may be already configured): API key is incorrect.
```

This means the OPIK configuration is trying to authenticate to OPIK Cloud with an invalid or missing API key.

---

## Root Cause Analysis

### Current Configuration

Your backend is set to use **OPIK Cloud** (not local):

```
OPIK_URL_OVERRIDE: https://www.comet.com/opik/api
OPIK_WORKSPACE: parth-d (YOUR workspace)
OPIK_PROJECT_NAME: rag-system
OPIK_API_KEY: ??? (Missing or invalid)
```

### What's Happening

1. System tries to connect to OPIK Cloud
2. It uses your API key to authenticate
3. API key is either:
   - ❌ Not set (empty)
   - ❌ Invalid/wrong format
   - ❌ Expired
   - ❌ For wrong workspace

---

## Quick Fix Options

### Option 1: Use Local OPIK (Recommended for Testing) ⭐

If you don't have a valid OPIK API key or want to test locally:

```bash
# Set to use LOCAL OPIK instead of cloud
set OPIK_ENABLED=true
set OPIK_URL_OVERRIDE=http://localhost:5173/api
set OPIK_API_KEY=local

# Then restart backend
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001
```

**Result:**
- ✅ OPIK will work locally (no cloud connection needed)
- ✅ No API key required
- ✅ Queries logged to local instance
- ⚠️ Only accessible at `http://localhost:5173`

---

### Option 2: Use Valid OPIK Cloud API Key (Best for Production)

If you have an OPIK Cloud account:

1. **Get your API key:**
   - Go to: https://www.comet.com/opik
   - Navigate to: **Settings** → **API Keys**
   - Copy your API key

2. **Set the API key:**
   ```bash
   set OPIK_API_KEY=<your_api_key_here>
   set OPIK_WORKSPACE=parth-d
   set OPIK_PROJECT_NAME=rag-system
   
   # Restart backend
   python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001
   ```

3. **Verify:**
   - Check logs for: `✅ OPIK initialization complete!`
   - Visit: https://www.comet.com/opik/workspace/parth-d/projects

---

### Option 3: Disable OPIK Temporarily

If you want to skip OPIK completely while you fix the key:

```bash
set OPIK_ENABLED=false

# Restart backend
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001
```

**Result:**
- ✅ Backend starts without OPIK errors
- ⚠️ Query auto-logging to OPIK won't work
- ✅ Local dataset storage still works

---

## Step-by-Step: Get Your OPIK API Key

### If You Have OPIK Cloud Account:

1. **Login to OPIK:**
   - Go to: https://www.comet.com/opik
   - Click your profile icon (top right)
   - Select: **Settings**

2. **Find API Keys:**
   - Left sidebar → **API Keys**
   - Or: **Account** → **API Keys**

3. **Create/Copy API Key:**
   - If no key exists, click **+ New API Key**
   - Copy the full key (starts with `opk_...`)

4. **Set in Environment:**
   ```bash
   set OPIK_API_KEY=opk_xxxxxxxxxxxxxxxxxxxxx
   ```

5. **Restart Backend:**
   ```bash
   # Ctrl+C in terminal
   python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001
   ```

6. **Check Logs:**
   ```
   INFO: OPIK_INIT: ✅ OPIK initialization complete!
   ```

---

## Current Environment Status

To check what's currently configured, run:

```powershell
# Check current settings
echo "OPIK_ENABLED: $env:OPIK_ENABLED"
echo "OPIK_WORKSPACE: $env:OPIK_WORKSPACE"
echo "OPIK_PROJECT_NAME: $env:OPIK_PROJECT_NAME"
echo "OPIK_URL_OVERRIDE: $env:OPIK_URL_OVERRIDE"
echo "OPIK_API_KEY: $(if ($env:OPIK_API_KEY) { '***SET***' } else { 'NOT SET' })"
```

Expected output:
```
OPIK_ENABLED: true
OPIK_WORKSPACE: parth-d
OPIK_PROJECT_NAME: rag-system
OPIK_URL_OVERRIDE: https://www.comet.com/opik/api
OPIK_API_KEY: ***SET*** (or NOT SET if missing)
```

---

## Decision Tree

```
┌─ Do you have OPIK Cloud account with valid API key?
│
├─ YES → Option 2: Set OPIK_API_KEY and restart
│        Expected: ✅ OPIK initialization complete!
│
├─ NO, want to test locally → Option 1: Set OPIK_URL_OVERRIDE to localhost
│        Expected: Works locally at http://localhost:5173
│
└─ NO, want to skip OPIK → Option 3: Set OPIK_ENABLED=false
         Expected: Backend works without OPIK
```

---

## Common Issues & Solutions

### Issue 1: "API key is incorrect" after setting key

**Solution:**
1. Check key format: Should start with `opk_`
2. Make sure you copied entire key (not truncated)
3. Verify workspace name matches
4. Restart backend with fresh terminal

```bash
# Clear and restart
Ctrl+C
# Close terminal completely
# Open new terminal
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001
```

---

### Issue 2: OPIK works but queries not appearing

**Cause:** Auto-logging might not be enabled

**Solution:** Ensure you have the latest code:
- Check [src/backend/main.py](src/backend/main.py) has "CHAT STEP 5" code
- If not, you need to apply the query auto-logging update

---

### Issue 3: Local OPIK not accessible

**Solution:**
1. Ensure OPIK is running locally:
   ```bash
   docker ps | grep opik
   # OR
   docker logs opik
   ```

2. If not running:
   ```bash
   docker-compose up -d opik  # or your docker setup
   ```

3. Access at: http://localhost:5173

---

## Quick Reference

| Scenario | Action | Environment |
|----------|--------|-------------|
| **Have OPIK API key** | Set API key | `OPIK_API_KEY=opk_...` |
| **Testing locally** | Use localhost | `OPIK_URL_OVERRIDE=http://localhost:5173/api` |
| **Skip OPIK** | Disable | `OPIK_ENABLED=false` |
| **Not sure** | Try local first | Option 1 |

---

## What To Do Now

### Recommended: Try Local OPIK First ⭐

```bash
# 1. Set to local
set OPIK_ENABLED=true
set OPIK_URL_OVERRIDE=http://localhost:5173/api
set OPIK_API_KEY=local

# 2. Restart backend
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001

# 3. Check logs for success
# Expected: OPIK_INIT: ✅ OPIK initialization complete!

# 4. Fire a test query in Streamlit
# http://localhost:8501

# 5. Check local OPIK
# http://localhost:5173
```

### OR: Get API Key from OPIK Cloud

1. Go to: https://www.comet.com/opik
2. Settings → API Keys
3. Copy key
4. Run: `set OPIK_API_KEY=<key_here>`
5. Restart backend

---

## Logs to Expect

### ✅ Success (Local OPIK):
```
OPIK_INIT: Starting OPIK initialization...
OPIK_INIT: Configuring OPIK (local=True, ...)
OPIK_INIT: ✅ OPIK initialization complete!
```

### ✅ Success (Cloud OPIK):
```
OPIK_INIT: Starting OPIK initialization...
OPIK_INIT: Configuring OPIK (local=False, workspace=parth-d)
OPIK_INIT: Connection validated - auth check passed
OPIK_INIT: ✅ OPIK initialization complete!
```

### ❌ Error (Invalid API Key):
```
OPIK_INIT: Configuration warning: API key is incorrect
OPIK_INIT: Auth check failed
```

---

## Next Step

Choose one approach above and let me know if you need help setting it up! 🚀
