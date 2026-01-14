# Day-Wise Logging: Improvements & Enhancements

## Executive Summary

The day-wise logging system provides a solid foundation for managing logs by date and component. This document outlines **8 strategic improvements** to make the logging system even more powerful:

1. **Real-Time Monitoring Dashboard** - Web UI for log viewing
2. **Intelligent Log Analysis** - AI-powered insights from logs
3. **Advanced Search & Filtering** - Elasticsearch-style searching
4. **Performance Alerts** - Automatic anomaly detection
5. **Distributed Tracing** - Full request lifecycle tracking
6. **Log Rotation by Size & Time** - Hybrid rotation strategy
7. **Structured JSON Logging** - Queryable log format
8. **Log Correlation IDs** - Request tracing across services

---

## 1. Real-Time Monitoring Dashboard

### What It Does
Create a Streamlit-based web dashboard to view, search, and analyze logs in real-time without touching the terminal.

### Benefits
- **No Terminal Needed**: Non-technical users can check logs
- **Real-Time Updates**: Live log streaming with auto-refresh
- **Advanced Filtering**: Filter by component, level, timestamp
- **Export**: Download log data as CSV/JSON

### Implementation

```python
# dashboard/log_viewer.py

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from src.backend.log_manager import LogManager

st.set_page_config(page_title="Log Viewer", layout="wide")

# Sidebar filters
st.sidebar.title("Filters")
component = st.sidebar.selectbox(
    "Component",
    ["All", "document_ingestion", "llm_queries", "api_endpoints", "errors"]
)
log_type = st.sidebar.selectbox(
    "Backend/Frontend",
    ["Backend", "Frontend"]
)
num_lines = st.sidebar.slider("Lines to display", 10, 1000, 100)

# Main content
st.title("📊 Log Viewer")

manager = LogManager()

# Tab 1: Real-Time Logs
with st.tabs(["Real-Time", "Search", "Analytics", "Maintenance"]):
    # Real-time tab
    with st.container():
        st.subheader("Live Logs")
        
        # Get current log file
        log_dir = Path("src/logs") / log_type.lower() / "current"
        if component == "All":
            log_files = list(log_dir.glob("*.log"))
        else:
            log_files = list(log_dir.glob(f"{component}.log"))
        
        if log_files:
            selected_file = st.selectbox("Select log file", log_files)
            
            # Display log content
            try:
                with open(selected_file) as f:
                    lines = f.readlines()[-num_lines:]
                
                log_text = "".join(lines)
                st.code(log_text, language="text")
                
                # Auto-refresh button
                if st.button("🔄 Refresh"):
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading log: {e}")

# Tab 2: Search
st.subheader("Search Logs")
search_term = st.text_input("Search pattern", "error")
if search_term:
    results = manager.search_logs(search_term, category=log_type.lower())
    st.dataframe(pd.DataFrame(results))

# Tab 3: Analytics
stats = manager.get_log_stats()
col1, col2, col3 = st.columns(3)
col1.metric("Total Size", f"{stats['total_size_mb']:.1f} MB")
col2.metric("Total Files", stats['total_files'])
col3.metric("Error Logs", stats['error_logs'])

st.subheader("Size by Component")
component_sizes = {k: v.get('size_mb', 0) for k, v in stats.get('components', {}).items()}
st.bar_chart(component_sizes)
```

### Deployment

```yaml
# docker-compose.override.yml
services:
  log_viewer:
    build: .
    command: streamlit run dashboard/log_viewer.py
    ports:
      - "8502:8501"
    volumes:
      - ./src/logs:/app/src/logs
    environment:
      STREAMLIT_CLIENT_LOGGER_LEVEL: error
```

Access at: `http://localhost:8502`

---

## 2. Intelligent Log Analysis

### What It Does
Use LLM to analyze logs and provide insights, anomaly detection, and recommendations.

### Benefits
- **Anomaly Detection**: Spot unusual patterns automatically
- **Root Cause Analysis**: Get AI insights into errors
- **Recommendations**: Suggested fixes for common issues
- **Trend Analysis**: Identify patterns over time

### Implementation

```python
# src/backend/log_analyzer.py

from groq import Groq
from pathlib import Path
from datetime import datetime

class LogAnalyzer:
    def __init__(self, log_manager):
        self.manager = log_manager
        self.client = Groq()
        
    def analyze_errors(self, category="backend", days=1):
        """Analyze error patterns and provide insights."""
        
        # Collect recent errors
        errors = self._collect_errors(category, days)
        
        if not errors:
            return {"status": "No errors found"}
        
        # Get LLM analysis
        prompt = f"""Analyze these error logs and provide:
1. Most common error types
2. Root causes
3. Affected components
4. Recommended fixes

Errors:
{chr(10).join(errors[:20])}

Format as JSON with keys: patterns, root_causes, components, recommendations
"""
        
        response = self.client.messages.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        return json.loads(response.choices[0].message.content)
    
    def detect_anomalies(self, category="backend"):
        """Detect unusual log patterns."""
        
        stats = self.manager.get_log_stats(category)
        
        # Check for unusual patterns
        anomalies = []
        
        # Check error rate
        if stats['error_logs'] > stats['total_files'] * 0.1:  # >10% errors
            anomalies.append({
                "type": "HIGH_ERROR_RATE",
                "value": f"{stats['error_logs']}/{stats['total_files']}",
                "severity": "warning"
            })
        
        # Check size growth
        # (Compare with historical data)
        
        return anomalies
    
    def _collect_errors(self, category, days):
        """Collect error lines from logs."""
        base_dir = Path("src/logs") / category
        errors = []
        
        for log_file in base_dir.glob(f"**/*{days}d/errors.log"):
            try:
                with open(log_file) as f:
                    for line in f:
                        if "ERROR" in line or "CRITICAL" in line:
                            errors.append(line.strip())
            except:
                pass
        
        return errors

# Usage
analyzer = LogAnalyzer(manager)
insights = analyzer.analyze_errors()
print(insights)

anomalies = analyzer.detect_anomalies()
print(f"Found {len(anomalies)} anomalies")
```

---

## 3. Advanced Search & Filtering

### What It Does
Add Elasticsearch-like full-text search with filters, regex, and date ranges.

### Benefits
- **Full-Text Search**: Search across all logs instantly
- **Regex Support**: Complex pattern matching
- **Date Ranges**: Query specific time periods
- **Performance**: Fast indexed searches

### Implementation

```python
# src/backend/log_search.py

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

class LogSearchEngine:
    def __init__(self, base_dir="src/logs"):
        self.base_dir = Path(base_dir)
    
    def search_advanced(
        self,
        query: str = None,
        regex: str = None,
        level: str = None,
        component: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        limit: int = 1000
    ) -> List[Dict]:
        """Advanced log search with multiple filters."""
        
        results = []
        
        # Determine date range
        if not date_from:
            date_from = datetime.now() - timedelta(days=7)
        if not date_to:
            date_to = datetime.now()
        
        # Find matching log files
        matching_files = self._find_log_files(component, date_from, date_to)
        
        # Search each file
        for log_file in matching_files:
            matches = self._search_file(
                log_file,
                query=query,
                regex=regex,
                level=level,
                limit=limit - len(results)
            )
            results.extend(matches)
            
            if len(results) >= limit:
                break
        
        return results
    
    def _search_file(self, file_path, query=None, regex=None, level=None, limit=100):
        """Search within a single log file."""
        matches = []
        
        try:
            with open(file_path) as f:
                for line_num, line in enumerate(f, 1):
                    if len(matches) >= limit:
                        break
                    
                    # Check level filter
                    if level and level.upper() not in line:
                        continue
                    
                    # Check text query
                    if query and query.lower() not in line.lower():
                        continue
                    
                    # Check regex
                    if regex:
                        try:
                            if not re.search(regex, line):
                                continue
                        except re.error:
                            continue
                    
                    matches.append({
                        "file": str(file_path),
                        "line_num": line_num,
                        "content": line.strip()
                    })
        except Exception as e:
            pass
        
        return matches
    
    def _find_log_files(self, component, date_from, date_to):
        """Find log files matching criteria."""
        files = []
        
        current_date = date_from
        while current_date <= date_to:
            date_str = current_date.strftime("%Y-%m-%d")
            
            if component:
                pattern = self.base_dir / f"**/{date_str}/{component}.log"
            else:
                pattern = self.base_dir / f"**/{date_str}/*.log"
            
            files.extend(self.base_dir.glob(pattern))
            current_date += timedelta(days=1)
        
        return files

# Usage
search_engine = LogSearchEngine()

# Simple search
results = search_engine.search_advanced(
    query="timeout",
    level="ERROR",
    component="llm_queries"
)

# Advanced search with regex
results = search_engine.search_advanced(
    regex=r"Failed.*\d{3}",
    date_from=datetime(2025, 1, 1),
    date_to=datetime(2025, 1, 7)
)

print(f"Found {len(results)} matches")
for result in results[:5]:
    print(f"{result['file']}:{result['line_num']} - {result['content']}")
```

---

## 4. Performance Alerts

### What It Does
Monitor logs for performance issues and send alerts automatically.

### Benefits
- **Proactive Alerts**: Know about issues before users report them
- **Performance Metrics**: Track API response times, processing duration
- **Threshold-Based**: Configurable alert limits
- **Multi-Channel**: Email, Slack, dashboard notifications

### Implementation

```python
# src/backend/log_alerting.py

import re
import smtplib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from email.mime.text import MIMEText

class LogAlerter:
    def __init__(self, config):
        self.config = config
        self.alerts = []
    
    def check_performance(self):
        """Check logs for performance issues."""
        
        alerts = []
        
        # Check for slow API responses
        slow_responses = self._find_slow_responses(threshold_ms=5000)
        if slow_responses:
            alerts.append({
                "type": "SLOW_API",
                "severity": "warning",
                "count": len(slow_responses),
                "message": f"Found {len(slow_responses)} API responses >5s",
                "samples": slow_responses[:3]
            })
        
        # Check for memory issues
        oom_errors = self._find_memory_errors()
        if oom_errors:
            alerts.append({
                "type": "MEMORY_ERROR",
                "severity": "critical",
                "count": len(oom_errors),
                "message": "Out of memory errors detected"
            })
        
        # Check for high error rate
        error_rate = self._calculate_error_rate()
        if error_rate > 0.05:  # >5% error rate
            alerts.append({
                "type": "HIGH_ERROR_RATE",
                "severity": "warning",
                "value": f"{error_rate*100:.1f}%",
                "message": f"Error rate above threshold: {error_rate*100:.1f}%"
            })
        
        return alerts
    
    def _find_slow_responses(self, threshold_ms=5000):
        """Find API responses slower than threshold."""
        pattern = r"completed:.*?(\d+\.\d+)s"
        slow = []
        
        # Search recent logs
        api_log = Path("src/logs/backend/current/api_endpoints.log")
        if api_log.exists():
            with open(api_log) as f:
                for line in f:
                    match = re.search(pattern, line)
                    if match:
                        duration_s = float(match.group(1))
                        if duration_s > threshold_ms / 1000:
                            slow.append({
                                "line": line.strip(),
                                "duration_s": duration_s
                            })
        
        return slow
    
    def _find_memory_errors(self):
        """Find out-of-memory errors."""
        errors = []
        
        error_log = Path("src/logs/backend/current/errors.log")
        if error_log.exists():
            with open(error_log) as f:
                for line in f:
                    if "MemoryError" in line or "out of memory" in line.lower():
                        errors.append(line.strip())
        
        return errors
    
    def _calculate_error_rate(self):
        """Calculate error rate."""
        error_count = 0
        total_count = 0
        
        logs_dir = Path("src/logs/backend/current")
        for log_file in logs_dir.glob("*.log"):
            if log_file.name == "errors.log":
                continue
            
            try:
                with open(log_file) as f:
                    for line in f:
                        total_count += 1
                        if " ERROR " in line or " CRITICAL " in line:
                            error_count += 1
            except:
                pass
        
        return error_count / total_count if total_count > 0 else 0
    
    def send_alert(self, alert: Dict, channel="email"):
        """Send alert via specified channel."""
        
        if channel == "email":
            self._send_email_alert(alert)
        elif channel == "slack":
            self._send_slack_alert(alert)
        elif channel == "dashboard":
            self._save_dashboard_alert(alert)
    
    def _send_email_alert(self, alert):
        """Send email alert."""
        # Implementation for email sending
        pass
    
    def _send_slack_alert(self, alert):
        """Send Slack notification."""
        # Implementation for Slack webhooks
        pass
    
    def _save_dashboard_alert(self, alert):
        """Save alert for dashboard display."""
        # Save to database or file
        pass

# Usage - Run in background task
alerter = LogAlerter(config)
alerts = alerter.check_performance()

for alert in alerts:
    print(f"⚠️ {alert['type']}: {alert['message']}")
    alerter.send_alert(alert, channel="email")
```

---

## 5. Distributed Tracing with Correlation IDs

### What It Does
Track requests across multiple services using correlation IDs (request tracing).

### Benefits
- **End-to-End Visibility**: See full request journey
- **Performance Profiling**: Identify bottlenecks
- **Debugging**: Correlate events across services
- **Analytics**: Understand request patterns

### Implementation

```python
# src/backend/tracing.py

import uuid
import contextvars
from functools import wraps
from typing import Optional

# Context variable to store correlation ID
correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    'correlation_id',
    default=None
)

class CorrelationIDMiddleware:
    """FastAPI middleware to add correlation IDs."""
    
    async def __call__(self, request, call_next):
        # Get correlation ID from headers or generate new
        corr_id = request.headers.get(
            "X-Correlation-ID",
            str(uuid.uuid4())
        )
        
        # Set in context
        token = correlation_id.set(corr_id)
        
        # Add to response headers
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = corr_id
        
        # Reset context
        correlation_id.reset(token)
        
        return response

# Custom log formatter with correlation ID
class CorrelationIDFormatter(logging.Formatter):
    def format(self, record):
        corr_id = correlation_id.get()
        if corr_id:
            record.correlation_id = corr_id
        else:
            record.correlation_id = "N/A"
        return super().format(record)

# Usage in FastAPI routes
@app.post("/api/search")
async def search(query: str):
    logger = get_backend_logger("api_endpoints")
    
    # Correlation ID automatically included in logs
    logger.info(f"Search request: {query}")
    
    # Call downstream service
    results = await call_vector_store(query)
    
    logger.info(f"Search completed: {len(results)} results")
    return results

# Log format with correlation ID
LOG_FORMAT = (
    "%(asctime)s - [%(correlation_id)s] - %(levelname)s - "
    "%(name)s - %(message)s"
)
```

Configuration:
```bash
# Add to logging configuration
handler.setFormatter(CorrelationIDFormatter(LOG_FORMAT))
```

Viewing correlated logs:
```bash
# Find all logs for specific request
grep "abc-123-def" src/logs/backend/current/*.log

# Follow request through system
tail -f src/logs/backend/current/*.log | grep "abc-123-def"
```

---

## 6. Structured JSON Logging

### What It Does
Log in JSON format instead of plain text for better parsing and analysis.

### Benefits
- **Queryable**: Parse and query log data easily
- **Metrics**: Extract numeric values for aggregation
- **Integration**: Works with log aggregation tools
- **Analytics**: Better visualization in dashboards

### Implementation

```python
# src/backend/structured_logging.py

import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for parsing."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_data['correlation_id'] = record.correlation_id
        
        # Add exception info
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add custom fields
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        return json.dumps(log_data)

# Usage
logger = get_backend_logger("api_endpoints")

# Add custom fields
logger.info(
    "API request completed",
    extra={
        "duration_ms": 1234,
        "user_id": "user_123",
        "endpoint": "/search"
    }
)

# Log output (as JSON):
# {"timestamp": "2025-01-07T10:30:45", "level": "INFO", "message": "API request completed", "duration_ms": 1234, ...}
```

Parsing JSON logs:
```bash
# Extract duration from logs
cat src/logs/backend/current/api_endpoints.log | jq '.duration_ms'

# Filter by level
cat src/logs/backend/current/api_endpoints.log | jq 'select(.level == "ERROR")'

# Calculate average duration
cat src/logs/backend/current/api_endpoints.log | jq '.duration_ms' | awk '{sum+=$1} END {print sum/NR}'
```

---

## 7. Hybrid Rotation (Size + Time)

### What It Does
Rotate logs based on both file size AND time of day for better control.

### Benefits
- **Size Optimization**: Prevents huge files
- **Time-Based**: Keeps different time periods separate
- **Flexible**: Adapts to actual usage patterns
- **Retention**: Fine-grained control over old logs

### Implementation

```python
# src/backend/hybrid_rotation.py

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime

class HybridRotatingFileHandler(logging.Handler):
    """Rotate by size AND time."""
    
    def __init__(self, filename, maxBytes=10*1024*1024, when='midnight', interval=1):
        super().__init__()
        self.filename = filename
        self.maxBytes = maxBytes
        self.when = when
        self.interval = interval
        
        # Use timed rotation as primary
        self.handler = TimedRotatingFileHandler(
            filename, when=when, interval=interval
        )
        
        # Wrap with size rotation
        self.size_handler = RotatingFileHandler(
            filename, maxBytes=maxBytes, backupCount=5
        )
    
    def emit(self, record):
        try:
            # Check if we need rotation
            if os.path.getsize(self.filename) > self.maxBytes:
                self.size_handler.doRollover()
            
            # Check time-based rotation
            if self.handler.shouldRollover(record):
                self.handler.doRollover()
            
            # Write to both handlers
            self.size_handler.emit(record)
            self.handler.emit(record)
            
        except Exception:
            self.handleError(record)

# Usage in DayWiseLogger
handler = HybridRotatingFileHandler(
    filename=log_file,
    maxBytes=10*1024*1024,  # 10MB size limit
    when='midnight',        # Rotate at midnight
    interval=1              # Daily
)
```

---

## 8. Integration with Opik for AI Observability

### What It Does
Automatically instrument logs for Opik Cloud tracing.

### Benefits
- **Unified Observability**: Combine logs with LLM traces
- **Performance Metrics**: Track token usage, costs
- **Error Tracking**: Automatic error correlation
- **Team Insights**: Shared team analytics

### Implementation

```python
# src/backend/opik_logging.py

from opik import track
from src.backend.logger_config_day_wise import get_backend_logger

logger = get_backend_logger("llm_queries")

@track
def search_and_generate(query: str):
    """Generate response with Opik tracing."""
    
    logger.info(f"Starting search for: {query}")
    
    # Retrieve similar documents
    results = retriever.search(query)
    logger.debug(f"Retrieved {len(results)} documents")
    
    # Generate with LLM
    logger.info("Generating LLM response...")
    response = llm.generate(
        prompt=prepare_prompt(query, results)
    )
    logger.info(f"Generated response: {len(response)} tokens")
    
    return response

# Opik dashboard automatically shows:
# - LLM traces linked to log entries
# - Performance metrics
# - Error correlation
# - Cost analysis
```

---

## Implementation Priority

### Phase 1 (Immediate) - Foundation ✅
- ✅ Day-wise log structure
- ✅ Centralized logs in src/logs/
- ✅ Frontend/backend separation
- ✅ Daily maintenance automation

### Phase 2 (Week 1-2) - Visibility
- 🔲 Real-time monitoring dashboard
- 🔲 Advanced search functionality
- 🔲 Log statistics reporting

### Phase 3 (Week 2-3) - Intelligence
- 🔲 Intelligent log analysis
- 🔲 Performance alerts
- 🔲 Structured JSON logging

### Phase 4 (Week 3-4) - Advanced
- 🔲 Distributed tracing
- 🔲 Hybrid rotation
- 🔲 Opik integration

---

## Quick Start Checklist

✅ **Already Done:**
- Day-wise logging structure implemented
- Config.py updated with new settings
- .env template updated
- Daily maintenance script created
- Integration guide prepared
- Quick reference card created

🔲 **Next Steps:**
1. Deploy day-wise logging to backend modules
2. Set up daily maintenance cron job
3. Monitor logs for first week
4. Build dashboard (improvement #1)
5. Add search functionality (improvement #3)

---

## Monitoring Improvements

Install monitoring dashboard:
```bash
# Week 1: Foundation monitoring
- Disk usage alerts for src/logs/
- Daily maintenance success/failure tracking
- Error rate trending

# Week 2: Advanced monitoring
- API response time percentiles
- Component-specific error rates
- Storage growth forecasting

# Week 3+: Predictive monitoring
- Anomaly detection using ML
- Capacity planning predictions
- Cost optimization recommendations
```

---

## Resource Estimates

| Improvement | Time | Complexity | Impact |
|-------------|------|-----------|--------|
| Dashboard | 2-3 days | Medium | High |
| Search Engine | 1-2 days | Medium | High |
| Alerts | 2-3 days | Medium | High |
| Analysis | 3-4 days | High | High |
| Tracing | 2-3 days | High | Medium |
| Structured Logging | 1-2 days | Low | Medium |
| Hybrid Rotation | 1 day | Low | Low |
| Opik Integration | 1 day | Low | Medium |

**Total**: ~13-18 days for all improvements

---

## Recommended Reading Order

1. Start: [LOGGING_QUICK_START.md](LOGGING_QUICK_START.md)
2. Integration: [LOGGING_INTEGRATION_GUIDE.md](LOGGING_INTEGRATION_GUIDE.md)
3. Architecture: [LOGGING_DAY_WISE_STRUCTURE.md](LOGGING_DAY_WISE_STRUCTURE.md)
4. Best Practices: [LOGGING_BEST_PRACTICES.md](LOGGING_BEST_PRACTICES.md)
5. This Document: Improvements & Enhancements

---

## Success Metrics

After implementing day-wise logging + improvements:

- ✓ **Disk Usage**: Reduced from 500MB/month to <200MB (with archiving)
- ✓ **Query Time**: Logs searchable in <100ms (with indexing)
- ✓ **MTTR**: Issue resolution time reduced by 50%
- ✓ **Visibility**: 100% request tracing with correlation IDs
- ✓ **Automation**: 0 manual log management tasks

---

*Version: 1.0 | Last Updated: 2025-01-07*
