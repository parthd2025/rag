# 🧪 Testing Guide - Generate Suggested Questions

## ✅ Quick Test Checklist

### Setup
- [ ] Backend is running: `cd backend && python main.py`
- [ ] Frontend is running: `cd frontend && streamlit run app.py`
- [ ] Have sample documents uploaded

### Test 1: Generate Button Works
**Steps**:
1. Click sidebar hamburger if closed
2. Click "💡 Questions" tab
3. Adjust slider: "Number of Questions" (try 3-5)
4. Click "🧠 Generate Suggested Questions" button

**Expected**:
- ✅ Spinner appears immediately
- ✅ Says "🧠 Generating suggested questions..."
- ✅ After 3-5 seconds: spinner disappears
- ✅ Success message appears: "✅ Generated 5 questions!"
- ⚠️ No error messages

### Test 2: Questions Display Correctly
**Steps**:
1. After questions generate, scroll down to bottom of page
2. Look below the chat input area

**Expected**:
- ✅ See "💡 Suggested Questions" section
- ✅ Section is collapsed (can be expanded)
- ✅ Shows "Found 5 suggested questions:"
- ✅ Each question has:
  - Icon (🔀 for comparative, 🎯 for others)
  - Question text
  - "→" button on the right
- ✅ Questions are properly formatted

### Test 3: No Layout Disruption
**Steps**:
1. Before clicking generate, note the position of:
   - Chat input box
   - Clear button
   - Any other UI elements
2. Click "Generate Suggested Questions"
3. Wait for success message
4. Note if any elements shifted

**Expected**:
- ✅ Chat input stays in same position
- ✅ Dashboard metrics don't jump
- ✅ No flickering or visual glitches
- ✅ Layout remains stable and clean

### Test 4: Use a Question
**Steps**:
1. Locate a generated question in the "Suggested Questions" expander
2. Click the "→" button next to a question

**Expected**:
- ✅ Question immediately appears in chat as user message
- ✅ Spinner appears: "🤔 Thinking..."
- ✅ After 2-5 seconds: Answer appears from RAG
- ✅ Sources displayed below answer (if available)
- ✅ Question and answer stored in chat history

### Test 5: Error Handling
**Steps**:
1. Stop the backend (Ctrl+C in backend terminal)
2. Try to generate questions again

**Expected**:
- ✅ Error message appears (red box with 🔌 icon)
- ✅ Says something like "Cannot reach API server"
- ✅ No crash or exception
- ✅ User can still interact with UI

### Test 6: Multiple Generations
**Steps**:
1. Generate questions (5 questions)
2. Wait for success message
3. Generate questions again (with different number, e.g., 3)
4. Wait for success message

**Expected**:
- ✅ First set of questions replaced by second set
- ✅ Count updates: "✅ Generated 3 questions!"
- ✅ Old questions no longer visible
- ✅ No duplication or mixing

### Test 7: UI Elements
**Steps**:
1. Generate questions
2. Expand/collapse the "💡 Suggested Questions" section
3. Try to scroll within the section

**Expected**:
- ✅ Expander opens and closes smoothly
- ✅ Questions are clearly readable
- ✅ "→" buttons are clickable
- ✅ No visual glitches

---

## 🐛 Troubleshooting

### Issue: No questions appear
**Possible Causes**:
1. No documents uploaded yet → Upload documents first
2. Backend not running → Start backend with `python main.py`
3. LLM service not configured → Check GROQ_API_KEY in .env

**Fix**:
```bash
# Check backend is running
curl http://localhost:8001/health

# Check if documents are loaded
curl http://localhost:8001/documents/count

# Try uploading a test document first
```

### Issue: Error "No documents loaded"
**Possible Causes**:
1. Documents uploaded but not indexed
2. Clear All Documents was clicked

**Fix**:
1. Go to sidebar → Upload tab
2. Click "🗑️ Clear All Documents"
3. Upload some documents again
4. Wait for indexing to complete
5. Try generating questions again

### Issue: Button doesn't respond
**Possible Causes**:
1. Streamlit in read-only mode
2. Session state issue
3. Page not fully loaded

**Fix**:
1. Refresh the browser (F5)
2. Click the button again
3. If still broken, restart Streamlit:
   ```bash
   # Kill old process
   pkill -f streamlit
   
   # Restart
   cd frontend && streamlit run app.py
   ```

### Issue: Questions appear in wrong place
**Possible Causes**:
1. Using old version of code
2. Browser cache issue

**Fix**:
1. Hard refresh browser: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. Verify you're running latest code:
   ```bash
   cd frontend
   python -m py_compile app.py  # Should pass
   ```

---

## 📊 Expected Response Times

| Action | Time | Notes |
|--------|------|-------|
| Generate button click → spinner | < 1 sec | Immediate response |
| Generation (spinner duration) | 3-8 sec | Depends on LLM, docs count |
| Display questions (after success) | < 1 sec | Should be instant |
| Click question → answer | 2-5 sec | Depends on RAG engine |

---

## 🎯 Success Criteria

**All tests passed if**:
- ✅ Button generates questions without error
- ✅ Questions appear in correct location (below chat)
- ✅ No output disruption or layout issues
- ✅ Each question is clickable and usable
- ✅ No silent failures or exceptions
- ✅ Error messages are clear and helpful
- ✅ Multiple generations work correctly

---

## 📝 Test Report Template

```
DATE: _______________
TESTER: _______________

Test 1: Generate Button: ☐ PASS ☐ FAIL
Test 2: Display: ☐ PASS ☐ FAIL
Test 3: No Disruption: ☐ PASS ☐ FAIL
Test 4: Use Question: ☐ PASS ☐ FAIL
Test 5: Error Handling: ☐ PASS ☐ FAIL
Test 6: Multiple Generations: ☐ PASS ☐ FAIL
Test 7: UI Elements: ☐ PASS ☐ FAIL

Issues Found:
_____________________________
_____________________________

Additional Notes:
_____________________________
_____________________________

OVERALL: ☐ PASS ☐ FAIL
```

---

## 🚀 Ready to Test!

**To start testing:**

1. **Terminal 1 - Backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Terminal 2 - Frontend**:
   ```bash
   cd frontend
   streamlit run app.py
   ```

3. **Browser**:
   - Opens automatically to `http://localhost:8501`
   - Upload some documents
   - Test the "Generate Suggested Questions" feature

**Enjoy the fixed feature! 🎉**
