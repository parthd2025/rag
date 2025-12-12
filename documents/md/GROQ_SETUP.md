# Groq API Setup Instructions

## Get Your Free Groq API Key

1. **Visit:** https://console.groq.com/keys
2. **Sign up** for a free account
3. **Create an API key** (if not already created)
4. **Copy the API key**

## Configure Your RAG System

### Option 1: Using .env File (Recommended)

1. Open `d:\RAG\.env` in a text editor
2. Replace `your_groq_api_key_here` with your actual API key:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. Save the file
4. Restart the backend

### Option 2: Using Environment Variable

```powershell
# In PowerShell, set the environment variable:
$env:GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Then run the backend:
python main.py
```

## Verify Setup

Once configured, start the backend and check for this message:
```
Groq client initialized with model: llama-3.3-70b-versatile
Ready!
```

## Models Available

Groq offers several fast inference models:
- `llama-3.3-70b-versatile` (Current) - Best for general use
- `llama-3.1-70b-versatile` - Previous version
- `mixtral-8x7b-32768` - Alternative model

## Free Tier Limits

- **Rate Limit:** 30 requests per minute (free tier)
- **Tokens per Minute:** 6000 TPM (free tier)
- No credit card required for free tier

For full details, visit: https://console.groq.com

