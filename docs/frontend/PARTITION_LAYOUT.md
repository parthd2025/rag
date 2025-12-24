# PARTITION LAYOUT - Two Column Design

## Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│ RAG Chatbot                                                      │
├──────────────────────┬─────────────────────────────────────────┤
│                      │                                          │
│  LEFT PANEL          │        RIGHT PANEL                      │
│  (1/3 width)         │        (2/3 width)                      │
│                      │                                          │
│  📋 Control Panel    │  🤖 RAG Chatbot                         │
│  ─────────────────   │  Powered by RAG...                      │
│                      │  ──────────────────────────────────     │
│  Upload Documents    │                                          │
│  ├─ Choose Files     │  📊 Document Chunks                     │
│  ├─ Drag/Drop Area   │  ├─ Number: 953                         │
│  ├─ File Preview     │  └─ Clear Button                        │
│  └─ Upload Button    │  ──────────────────────────────────     │
│                      │                                          │
│  Upload Validation   │  📋 Session Overview                    │
│  ├─ File Size        │  ├─ Questions: 0                        │
│  └─ Status           │  ├─ Duration: 0.3m                      │
│                      │  └─ Avg Response: 0.00s                 │
│  Document Chunks     │  ──────────────────────────────────     │
│  ├─ Total: 953       │                                          │
│  └─ Clear All        │  💬 Ask a Question                      │
│                      │  ├─ Input Field                         │
│                      │  ├─ Send Button                         │
│                      │  └─ Clear Button                        │
│                      │                                          │
│                      │  Chat History:                          │
│                      │  ├─ You: ...                            │
│                      │  ├─ Assistant: ...                      │
│                      │  └─ Sources                             │
│                      │                                          │
└──────────────────────┴─────────────────────────────────────────┘
```

---

## Component Breakdown

### LEFT PANEL (Control Panel)

**Upload Documents**
- File uploader widget
- Drag & drop area
- File type selector (PDF, DOCX, TXT, etc.)
- File preview (name + size)

**Upload Validation**
- File size display
- Validation status
- Upload button (primary, red)

**Document Chunks**
- Shows total chunks count
- Clear all documents button

### RIGHT PANEL (Main Content)

**Header**
- Title "RAG Chatbot"
- Subtitle "Powered by RAG, Semantic Transformers, and Groq"

**Document Chunks**
- Large display of chunk count
- Clear button (secondary)

**Session Overview**
- Metrics: Questions, Duration, Avg Response
- All stats in 3-column layout

**Ask a Question**
- Text input field
- Send button (arrow icon)
- Clear chat button

**Chat History**
- User messages
- Assistant responses
- Expandable sources

---

## Column Ratio

```
Left Panel:  1 unit (30%)
Right Panel: 2.5 units (70%)

Total = 3.5 units = 100%
```

---

## Features

✅ **Left Control Panel**
- File upload with drag & drop
- File validation display
- Document chunk counter
- Clear all function

✅ **Right Main Content**
- Large document chunk display
- Session overview metrics
- Chat interface
- Message history
- Source display

✅ **Professional Look**
- Clean partition
- Professional spacing
- Clear sections
- Easy to navigate

---

## Code Structure

```python
left, right = st.columns([1, 2.5])

with left:
    # Control Panel
    - Upload section
    - Validation section
    - Document chunks display

with right:
    # Main Content
    - Header
    - Document chunks display
    - Session metrics
    - Chat interface
    - Message history
```

---

## Visual Flow

```
User Action Flow:

1. Left Panel: Upload file
   ↓
2. Upload Validation: Show file info
   ↓
3. Click Upload Button
   ↓
4. Right Panel: Update chunk count
   ↓
5. Right Panel: Ask question
   ↓
6. Chat: Show answer + sources
   ↓
7. Left Panel: Clear All (optional)
```

---

## Colors & Styling

- **Left Panel**: Control Panel section (sidebar style)
- **Right Panel**: Main content (light background)
- **Upload Button**: Primary (red/green)
- **Clear Buttons**: Secondary (gray/muted)
- **Metrics**: Highlighted display
- **Chat**: User/Assistant differentiation

---

## Responsive

```
Desktop (Wide):
┌────┬────────────────┐
│ L  │      R         │
│ E  │    (70%)       │
│ F  │                │
│ T  │                │
│    │                │
└────┴────────────────┘

Tablet (Medium):
Two columns still visible, slightly cramped

Mobile (Narrow):
Might need to stack columns
(Streamlit handles this)
```

---

## Interaction Points

### Left Panel
- File uploader
- Upload button (primary)
- Clear all button (secondary)

### Right Panel
- Text input (question)
- Send button
- Clear chat button
- Message sources (expandable)

---

## Content Sections

**Left (Persistent)**
- Always visible
- For control & management
- File operations
- Stats display

**Right (Dynamic)**
- Shows results
- Chat interface
- Session info
- Message history

---

## Metrics Display

```
Session Overview:
┌─────────┬──────────┬────────────────┐
│Questions│ Duration │ Avg Response   │
├─────────┼──────────┼────────────────┤
│    0    │  0.3m    │   0.00s        │
└─────────┴──────────┴────────────────┘
```

---

## Ready to Use

The partition layout is now active!

```bash
streamlit run app.py
```

Features:
- ✅ Left control panel (30%)
- ✅ Right main content (70%)
- ✅ Upload & validation
- ✅ Document chunk display
- ✅ Session metrics
- ✅ Chat interface
- ✅ Professional design
