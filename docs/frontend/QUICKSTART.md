# 🚀 Quick Start Guide - Frontend

## 5-Minute Setup

### Step 1: Navigate to Frontend

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed streamlit-1.32.2 requests-2.32.3 python-dotenv-1.0.1
```

### Step 3: Verify Backend is Running

Open another terminal:
```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Step 4: Start Frontend

Back in frontend terminal:
```bash
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Step 5: Open in Browser

Visit: **http://localhost:8501**

---

## What You'll See

### First Load
1. **Connection Status** - Shows if backend is connected ✅
2. **Four Tabs** - Chat, Documents, Quiz, Settings
3. **Sidebar** - Quick stats and settings

### Try These Actions

1. **Upload a Document** (Documents tab)
   - Click upload
   - Select a PDF or TXT file
   - Wait for processing

2. **Ask a Question** (Chat tab)
   - Type "What is this document about?"
   - Press Send
   - See answer with sources

3. **Generate Quiz** (Quiz tab)
   - Click "Generate Quiz"
   - Answer the questions
   - View results

---

## Environment Setup

Create `.env` file in project root if not exists:

```env
GROQ_API_KEY=gsk_your_key_here
API_URL=http://localhost:8001
REQUEST_TIMEOUT=180
```

---

## Port Information

| Service | Port | URL |
|---------|------|-----|
| Backend | 8001 | http://localhost:8001 |
| Frontend | 8501 | http://localhost:8501 |

---

## Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Start frontend
streamlit run app.py

# Stop frontend
Ctrl + C

# View logs
tail -f ../logs/frontend_logs/*.log

# Clear cache
rm -rf .streamlit
```

---

## Common Issues & Solutions

### ❌ "Cannot connect to API"
```bash
# Check backend is running
curl http://localhost:8001/health

# If fails, start backend
cd ../backend
python main.py
```

### ❌ "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### ❌ "Port 8501 already in use"
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### ❌ "Slow response"
- Check backend performance
- Verify internet connection
- Try reducing documents

---

## Directory Structure

```
frontend/
├── app.py                    ← Main app
├── config.py               ← Settings
├── requirements.txt        ← Dependencies
├── README.md              ← Full docs
├── .streamlit/
│   └── config.toml        ← Streamlit config
├── components/
│   ├── chat.py
│   ├── documents.py
│   ├── quiz.py
│   └── system_info.py
└── utils/
    ├── api_client.py
    └── ui_components.py
```

---

## Testing the Frontend

### Manual Testing Checklist

- [ ] Frontend loads without errors
- [ ] Backend connection shows ✅
- [ ] Can upload document
- [ ] Can see document stats
- [ ] Can ask question and get answer
- [ ] Can generate quiz
- [ ] Can view system info
- [ ] Responsive on mobile

---

## Next Steps

1. **Upload Documents** - Start with small test files
2. **Ask Questions** - Try different phrasing
3. **Generate Quiz** - Test knowledge assessment
4. **Customize** - Edit config.py for your needs
5. **Deploy** - Use Streamlit Cloud or Docker

---

## Tips & Best Practices

✅ **DO:**
- Upload one document at a time initially
- Use clear, specific questions
- Check API connection status
- Monitor backend logs

❌ **DON'T:**
- Upload huge files (>10MB)
- Ask vague questions
- Close backend while using frontend
- Edit files while frontend is running

---

## Performance Optimization

### For Fast Performance:
1. Keep documents under 5MB
2. Use fewer top_k results (3-5)
3. Clear old data periodically
4. Monitor vector store size

### Storage Cleanup:
```bash
# Clear all data
# Use "Clear All Data" in Documents tab
# Or: curl -X DELETE http://localhost:8001/clear
```

---

## Deployment Ready

This frontend is production-ready with:
- ✅ Error handling
- ✅ Loading states
- ✅ Session management
- ✅ Responsive design
- ✅ Performance optimization
- ✅ Professional UI/UX

---

**Ready to go? Start your journey now!** 🚀
