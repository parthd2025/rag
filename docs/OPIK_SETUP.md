# Opik Local Setup Guide

## Prerequisites
- Docker Desktop installed and running on Windows
- Git installed

## Setup Steps

### 1. Start Docker Desktop
Make sure Docker Desktop is running before proceeding.

### 2. Clone Opik Repository (First Time Only)
The Opik repository has already been cloned to `D:\RAG\opik`.

### 3. Start Opik Server
```powershell
cd D:\RAG\opik
.\opik.ps1
```

### 3. Verify Opik is Running
```bash
docker-compose -f docker-compose.opik.yml ps
```

### 4. Access Opik UI
Open your browser and navigate to: http://localhost:5173

### 5. Install Opik Python Client
```bash
pip install opik
```

### 6. Configure Environment Variables
Add the following to your `.env` file or load from `.env.opik`:
```
OPIK_API_KEY=local
OPIK_WORKSPACE=default
OPIK_PROJECT_NAME=rag-system
OPIK_URL_OVERRIDE=http://localhost:5173
OPIK_ENABLED=true
```

### 7. Stop Opik Server
```powershell
cd D:\RAG\opik
.\opik.ps1 --stop
```

### 8. View Logs
```powershell
docker logs opik-backend -f
# Or view all Opik containers
docker ps --filter "name=opik" --format "table {{.Names}}\t{{.Status}}"
```

## Integration with RAG System


# Configure for local Opik instance
opik.configure(use_local=True)

# Track a function
@opik.

# Track a function
@track()
def query_rag(question: str):
    # Your RAG logic here
    return response
```

### LangChain Integration
```python
from langchain.callbacks import OpikCallbackHandler

callback = OpikCallbackHandler()

# Use with LangChain chains
chain.run(query, callbacks=[callback])
```

## Troubleshooting

### Docker Desktop Not Running
Error: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`

**Solution:** Start Docker Desktop application

### Port Already in Use
If ports 5173 or 8080 are already in use, modify `docker-compose.opik.yml`:
```yaml
ports:
  - "5174:5173"  # Change external port
  - "8081:8080"  # Change external port
```

### Container Health Check Failing
Check container logs:
```bash
docker logs opik-server
```

## Next Steps
1. Start Docker Desktop
2. Run: `docker-compose -f docker-compose.opik.yml up -d`
3. Wait 30-40 seconds for the server to start
4. Access UI at http://localhost:5173
5. Install Python client: `pip install opik`
