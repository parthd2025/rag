# Frontend - Developer Guide

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│        Streamlit Framework          │
├─────────────────────────────────────┤
│         app.py (Main Entry)         │
├─────────────────────────────────────┤
│  Components Layer                   │
│  ├─ chat.py                         │
│  ├─ documents.py                    │
│  ├─ quiz.py                         │
│  └─ system_info.py                  │
├─────────────────────────────────────┤
│  Utils Layer                        │
│  ├─ api_client.py                   │
│  └─ ui_components.py                │
├─────────────────────────────────────┤
│  Backend API (FastAPI)              │
├─────────────────────────────────────┤
│  RAG Engine & Vector Store          │
└─────────────────────────────────────┘
```

## 🔄 Data Flow

```
User Input (Streamlit UI)
    ↓
Component Processing
    ↓
API Client (HTTP Request)
    ↓
Backend Processing
    ↓
API Response
    ↓
Component Rendering
    ↓
UI Display (Streamlit Output)
```

## 🧩 Component Responsibilities

### app.py
- Main application logic
- Tab management
- Session state initialization
- Sidebar rendering
- Connection management

### components/chat.py
- Chat interface
- Message history
- Source display
- Quick actions

### components/documents.py
- File upload interface
- Document statistics
- Data management
- Clear functions

### components/quiz.py
- Quiz generation
- Question display
- Answer tracking
- Results display

### components/system_info.py
- System dashboard
- Configuration display
- Health status
- Help documentation

### utils/api_client.py
- HTTP communication
- Retry logic
- Error handling
- Request validation
- Response parsing

### utils/ui_components.py
- CSS injection
- Component library
- Custom styling
- Reusable elements

---

## 🛠️ Development Workflow

### Adding a New Feature

1. **Create Component**
```python
# components/my_feature.py
def render_my_feature(api_client):
    st.markdown("### 🆕 My Feature")
    # Component code
```

2. **Import in app.py**
```python
from components.my_feature import render_my_feature
```

3. **Add to Tab**
```python
with tab_new:
    render_my_feature(api_client)
```

### Modifying UI Components

1. Edit `utils/ui_components.py`
2. Add to CSS section
3. Create function
4. Use in components

### Updating API Integration

1. Add method to `APIClient` class
2. Handle errors appropriately
3. Use in components via `api_client`

---

## 🔌 API Integration Pattern

```python
# In any component
def my_component(api_client):
    if st.button("Do something"):
        try:
            response = api_client.my_method(params)
            st.success("Success!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
```

---

## 📝 Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
```

Logs go to: `logs/frontend_logs/app.log`

---

## ⚙️ Configuration Management

All settings in `config.py`:
- API URLs
- Timeouts
- File sizes
- Feature flags
- UI strings
- Colors
- Performance settings

---

## 🧪 Testing

### Manual Testing
1. Start backend
2. Start frontend
3. Test each component
4. Test error states
5. Test edge cases

### Automated Testing (TODO)
```bash
pip install pytest pytest-streamlit
pytest tests/
```

---

## 📊 Performance Optimization

### Current Optimizations
- Streamlit @st.cache_resource for API client
- Lazy component loading
- Efficient session state
- CSS caching
- Minimal re-renders

### Potential Improvements
- Add @st.cache_data for queries
- Implement pagination
- Add websockets for real-time
- Optimize large file uploads
- Add image optimization

---

## 🔒 Security Considerations

- ✅ Input validation
- ✅ Error sanitization
- ✅ CORS enabled
- ✅ No sensitive data in UI
- ✅ Session isolation

### Enhanced Security
- Add rate limiting
- Implement auth
- Add HTTPS enforcement
- Add input sanitization

---

## 📱 Responsive Design

### Breakpoints
- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

### Current Support
- ✅ Desktop
- ✅ Tablet
- ✅ Mobile

---

## 🎨 Theming

### Change Theme
1. Edit `COLORS` in config.py
2. Update CSS variables
3. Test across components

### Custom CSS
Add to `ui_components.py` render_custom_css():
```python
css = """
<style>
.my-custom-class {
    /* styles */
}
</style>
"""
```

---

## 🚀 Performance Metrics

### Target Metrics
- Page load: < 1s
- Tab switch: < 500ms
- Component render: < 100ms
- API response: < 10s
- File upload: < 60s

### Monitoring
Check browser dev tools:
- Network tab for API calls
- Console for errors
- Performance tab for rendering

---

## 🐛 Debugging

### Enable Debug Mode
```bash
streamlit run app.py --logger.level=debug
```

### Check Logs
```bash
# Backend logs
tail -f logs/backend_logs/*.log

# Frontend console
# Press Ctrl+Shift+I in browser
```

### Common Issues

1. **API not responding**
   - Check backend is running
   - Check API_URL in .env
   - Check firewall

2. **Slow performance**
   - Check network
   - Check backend load
   - Reduce vector store size

3. **Component errors**
   - Check browser console
   - Check Python output
   - Check logs

---

## 📚 Code Style

### Python Style Guide
- Use type hints
- Add docstrings
- Follow PEP 8
- Use meaningful names
- Add comments

### Example
```python
def render_my_component(api_client: APIClient) -> None:
    """Render professional component.
    
    Args:
        api_client: API client instance
    """
    st.markdown("### My Component")
```

---

## 🔄 Version Control

### Commit Messages
```
[component] Brief description

- Detailed changes
- What was added
- Why it was changed
```

---

## 📦 Dependencies

All in `requirements.txt`:
```
streamlit==1.32.2
requests==2.32.3
python-dotenv==1.0.1
pydantic==2.5.0
```

---

## 🚢 Deployment

### Local Deployment
```bash
streamlit run app.py
```

### Streamlit Cloud
```bash
# Push to GitHub
# Connect to Streamlit Cloud
# Deploy automatically
```

### Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

---

## 📈 Scaling Considerations

### Database
- Consider persistent storage
- Implement caching layer
- Add database connection pooling

### Performance
- Add CDN for assets
- Implement response caching
- Use load balancer

### Architecture
- Separate services
- Implement microservices
- Add message queue

---

## 🎓 Learning Resources

- Streamlit: https://docs.streamlit.io
- Python: https://python.org
- UI/UX: https://www.nngroup.com
- Design: https://material.io

---

## 📞 Support

For questions about:
- **Architecture**: See this file
- **UI/UX**: See README.md
- **Setup**: See QUICKSTART.md
- **Implementation**: See IMPLEMENTATION_COMPLETE.md

---

**Happy coding! Build amazing features!** 🚀
