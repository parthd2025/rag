# ⚡ OPIK API Key Fix - Quick Commands

## The Issue
```
OPIK_INIT: Configuration warning (may be already configured): API key is incorrect.
```

---

## Fix #1: Use Local OPIK (No Key Needed) ⭐

```powershell
# Set environment variables
set OPIK_ENABLED=true
set OPIK_URL_OVERRIDE=http://localhost:5173/api
set OPIK_API_KEY=local

# Restart backend
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001
```

**Then:**
- Check logs: Should see ✅ `OPIK_INIT: ✅ OPIK initialization complete!`
- Access local OPIK: http://localhost:5173
- Fire test query in Streamlit

---

## Fix #2: Use OPIK Cloud API Key (Recommended)

1. **Get API key:**
   - Go to: https://www.comet.com/opik
   - Click profile icon → Settings → API Keys
   - Copy your key

2. **Set it:**
   ```powershell
   set OPIK_API_KEY=opk_xxxxxxxxxxxxxxxxxxxxx
   
   # Verify other settings
   set OPIK_WORKSPACE=parth-d
   set OPIK_PROJECT_NAME=rag-system
   ```

3. **Restart:**
   ```powershell
   python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001
   ```

---

## Fix #3: Skip OPIK (Temporary)

```powershell
set OPIK_ENABLED=false

python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001
```

Backend works, but OPIK logging disabled.

---

## Check Current Status

```powershell
echo "OPIK_ENABLED: $env:OPIK_ENABLED"
echo "OPIK_WORKSPACE: $env:OPIK_WORKSPACE"
echo "OPIK_PROJECT_NAME: $env:OPIK_PROJECT_NAME"
echo "OPIK_URL_OVERRIDE: $env:OPIK_URL_OVERRIDE"
echo "OPIK_API_KEY: $(if ($env:OPIK_API_KEY) { '***SET***' } else { 'NOT SET' })"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key still invalid | Make sure full key copied (starts with `opk_`) |
| Still won't connect | Try local OPIK (Fix #1) |
| Local OPIK not running | Ensure Docker container is running |
| Workspace error | Verify `OPIK_WORKSPACE=parth-d` |

---

## Verify It Works

1. ✅ Restart backend
2. ✅ Check logs for: `✅ OPIK initialization complete!`
3. ✅ Fire query in Streamlit
4. ✅ See query in local OPIK or OPIK Cloud

---

**Recommended:** Start with **Fix #1 (Local OPIK)** - quickest way to test! 🚀
