# RAG Chatbot - Simplified Frontend Guide

## Quick Start (2 minutes)

### 1. Install Dependencies
```bash
cd frontend
pip install streamlit==1.32.2 requests==2.32.3 python-dotenv==1.0.1
```

### 2. Start Backend
```bash
cd backend
python main.py
```

### 3. Start Frontend
```bash
cd frontend
streamlit run app.py
```

Open: http://localhost:8501

---

## Simple Navigation

**Left Sidebar** → Choose: Chat, Upload, Quiz, or Settings

```
Navigation
  📍 Chat       - Ask questions
  📍 Upload     - Add documents  
  📍 Quiz       - Test knowledge
  📍 Settings   - System info
```

---

## How It Works

### Chat Tab
1. Upload documents first (Upload tab)
2. Type a question
3. Get answers with sources

### Upload Tab  
1. Select a file (PDF, DOCX, TXT, etc.)
2. Click Upload
3. Wait for processing

### Quiz Tab
1. Choose number of questions (1-20)
2. Answer multiple choice
3. View score

### Settings Tab
1. Check system status
2. Read help documentation
3. View API info

---

## File Structure

```
frontend/
  app.py                 - Main application (165 lines)
  config.py              - Configuration
  components/
    chat.py             - Chat interface (65 lines)
    documents.py        - Document upload
    quiz.py             - Quiz system
    system_info.py      - System dashboard
  utils/
    api_client.py       - Backend API
    ui_components.py    - UI styles
```

---

## What Changed

**Before:** Complex tab-based UI with lots of features
**Now:** Simple single-page navigation with:
- Sidebar for easy navigation
- Linear workflow (Upload → Chat → Quiz)
- Minimal buttons and options
- Clear, direct interface

---

## Troubleshooting

### "Cannot connect to API"
- Check backend is running: `cd backend && python main.py`
- Verify API_URL in config.py is correct

### "No documents uploaded"
- Go to Upload tab
- Select file and click Upload
- Wait for "Success" message

### "Quiz won't start"
- Ensure documents uploaded first
- Check documents tab shows chunks

---

## Total Lines of Code

- **app.py**: 165 lines (down from 521)
- **chat.py**: 65 lines (down from 138)
- **documents.py**: 50 lines (simplified)
- **quiz.py**: 60 lines (simplified)
- **Total UI**: ~300 lines (superfast, easy to understand)

---

**That's it! Simple, fast, and easy to use.**
