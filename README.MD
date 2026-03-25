# NewsAI — Intelligent News Agent

<div align="center">

![NewsAI](https://img.shields.io/badge/NewsAI-Intelligent%20News%20Agent-1A2340?style=for-the-badge&logo=rss&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-llama3.2-FF6B35?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**An AI-powered news summarization and explanation agent that runs 100% locally.**
Fetch real articles → Analyze with a local LLM → Get summaries, explanations, sentiment and key points.

[Features](#-features) · [Architecture](#-architecture) · [Installation](#-installation) · [Usage](#-usage) · [API Reference](#-api-reference) · [Project Structure](#-project-structure)

</div>

---

## ✨ Features

- 🔍 **Real-time news fetching** from BBC, Reuters, The Hindu, Times of India (RSS) and GNews API
- 🤖 **Local AI analysis** using llama3.2 via Ollama — no cloud, no cost, no data sharing
- 📝 **Structured output** per article: Summary · Plain explanation · Category · Sentiment · Key points
- 🕓 **Search history** stored in browser localStorage — persists across sessions
- ⭐ **Topic recommendations** and trending chips for quick exploration
- 🌗 **Light / Dark mode** toggle with preference saved across sessions
- 🔄 **Sentiment sort** — reorder results by Positive / Negative / Neutral
- 🔒 **100% private** — no user data or article content ever leaves your machine
- 💸 **Completely free** — no paid APIs, no subscriptions required

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (User)                          │
│              http://localhost:5000                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP POST /search
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Flask Frontend  (port 5000)                        │
│         frontend/app.py  ·  templates/  ·  static/              │
│  Serves HTML · Proxies API requests to FastAPI backend          │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP POST /analyze
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend  (port 8000)                       │
│         backend/main.py  ·  news_fetcher.py  ·  ai_agent.py    │
│  Validates input · Fetches news · Orchestrates AI analysis      │
└──────────┬────────────────────────────┬────────────────────────┘
           │                            │
           ▼                            ▼
┌──────────────────┐         ┌──────────────────────────────────┐
│  News Sources    │         │   Ollama  (port 11434)           │
│  ─────────────  │         │   Model: llama3.2 (2 GB)         │
│  RSS Feeds       │         │   Runs 100% locally              │
│  · BBC News      │         │   No internet required for AI    │
│  · Reuters       │         └──────────────────────────────────┘
│  · The Hindu     │
│  · Times of India│
│  GNews API (opt) │
└──────────────────┘
```

### How it works

| Step | What happens |
|------|-------------|
| 1 | User enters a topic and clicks **Analyze topic** |
| 2 | Browser sends `POST /search` to Flask with `{ topic, num_articles, source }` |
| 3 | Flask proxies the request to FastAPI `POST /analyze` |
| 4 | FastAPI fetches articles from RSS feeds or GNews API based on topic |
| 5 | For each article, a structured prompt is sent to Ollama (llama3.2) |
| 6 | llama3.2 returns summary, explanation, category, sentiment, key points as JSON |
| 7 | FastAPI assembles the full result and returns it to Flask → browser |
| 8 | JavaScript renders article cards and saves the search to history |

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend server | Flask 3.0 | Serves HTML pages, proxies API requests |
| UI | HTML5 + CSS3 + Vanilla JS | Dashboard interface, light/dark theme |
| Backend API | FastAPI | REST API, request validation, orchestration |
| API server | Uvicorn | ASGI server running FastAPI |
| AI model | llama3.2 (2 GB) | News summarization and explanation |
| LLM runner | Ollama | Runs llama3.2 locally on port 11434 |
| News fetching | feedparser + requests | RSS parsing and GNews API calls |
| Validation | Pydantic v2 | FastAPI request body validation |
| Environment | python-dotenv | Reads `.env` file for API keys |
| Text cleaning | BeautifulSoup4 | Strips HTML from article content |

---

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.9+** installed
- **Ollama** installed — download from [https://ollama.com](https://ollama.com)
- **4 GB+ free RAM** (llama3.2 needs ~2 GB)
- **Git** (optional, for cloning)

Check your Python version:
```bash
python --version
```

Check Ollama is installed:
```bash
ollama --version
```

---

## 🚀 Installation

### Step 1 — Clone the repository

```bash
git clone https://github.com/yourusername/newsai.git
cd newsai
```

Or download and extract the ZIP, then navigate into the folder.

---

### Step 2 — Pull the AI model

```bash
ollama pull llama3.2
```

> This downloads the llama3.2 model (~2 GB). Only needs to be done once.

Verify the model is available:
```bash
ollama list
```

You should see `llama3.2` in the output.

---

### Step 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install fastapi uvicorn flask requests feedparser beautifulsoup4 python-dotenv pydantic
```

---

### Step 4 — Configure environment (optional)

Create a `.env` file inside the `backend/` folder:

```bash
# backend/.env
GNEWS_API_KEY=your_gnews_api_key_here
```

> **GNews API key is optional.** If not provided, the app automatically falls back to free RSS feeds.
> Get a free key (100 requests/day) at [https://gnews.io](https://gnews.io)

---

## ▶️ Running the Project

You need **two terminals** open simultaneously.

### Terminal 1 — Start the FastAPI Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### Terminal 2 — Start the Flask Frontend

```bash
cd frontend
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

### Open in browser

```
http://localhost:5000
```

---

## 🧪 Verify Everything is Working

### Check FastAPI is running
```bash
curl http://localhost:8000/
```
Expected: `{"message": "News AI Agent is running"}`

### Check Ollama is running
```bash
ollama list
```
Should show `llama3.2` in the list.

### Test Ollama manually
```bash
ollama run llama3.2 "Summarize this in one line: AI is transforming industries rapidly."
```

### Test the full API manually
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"topic": "Artificial Intelligence", "num_articles": 2}'
```

---

## 📁 Project Structure

```
newsai/
│
├── backend/
│   ├── main.py              # FastAPI app — /analyze endpoint
│   ├── news_fetcher.py      # RSS + GNews article fetching
│   ├── ai_agent.py          # Ollama LLM integration + JSON parser
│   ├── .env                 # API keys (create this manually)
│   └── requirements.txt     # Python dependencies (backend)
│
├── frontend/
│   ├── app.py               # Flask server
│   ├── templates/
│   │   └── index.html       # Main dashboard page
│   └── static/
│       ├── style.css        # Full UI styles (light + dark theme)
│       └── script.js        # All JS — search, history, cards, theme
│
├── requirements.txt         # Combined Python dependencies
└── README.md                # This file
```

---

## 🔌 API Reference

### `POST /analyze`

Analyzes news articles for a given topic.

**URL:** `http://localhost:8000/analyze`

**Request body:**
```json
{
  "topic": "Artificial Intelligence",
  "num_articles": 5,
  "source": "rss"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | ✅ Yes | — | News topic to search for |
| `num_articles` | integer | ❌ No | 5 | Number of articles to fetch (1–8) |
| `source` | string | ❌ No | `"rss"` | `"rss"` for RSS feeds, `"gnews"` for GNews API |

**Response:**
```json
{
  "topic": "Artificial Intelligence",
  "total": 3,
  "results": [
    {
      "title": "Article headline here",
      "url": "https://source.com/article",
      "source": "BBC",
      "analysis": {
        "summary": "Three sentence summary of the article content.",
        "explanation": "Simple explanation for a non-expert reader.",
        "category": "Technology",
        "sentiment": "Positive",
        "key_points": [
          "First key takeaway from the article",
          "Second key takeaway",
          "Third key takeaway"
        ]
      }
    }
  ]
}
```

**Possible `category` values:**
`Politics` · `Technology` · `Business` · `Health` · `Sports` · `Science` · `World` · `Environment`

**Possible `sentiment` values:**
`Positive` · `Negative` · `Neutral`

---

## ⚙️ Configuration

### Changing the AI model

In `backend/ai_agent.py`, change the `MODEL` variable:

```python
# Default
MODEL = "llama3.2"

# Lighter and faster (less RAM)
MODEL = "phi3"

# More powerful (needs more RAM)
MODEL = "llama3"
```

Available models and their requirements:

| Model | Size | RAM needed | Speed |
|-------|------|-----------|-------|
| `phi3` | 2.3 GB | 4 GB | Very fast |
| `llama3.2` | 2.0 GB | 4 GB | Fast ✅ Recommended |
| `mistral` | 4.1 GB | 6 GB | Medium |
| `llama3` | 4.7 GB | 8 GB | Slower |

To pull a different model:
```bash
ollama pull phi3
ollama pull mistral
ollama pull llama3
```

---

### Adding more RSS sources

In `backend/news_fetcher.py`, add to the `RSS_FEEDS` dictionary:

```python
RSS_FEEDS = {
    "BBC":       "http://feeds.bbci.co.uk/news/rss.xml",
    "Reuters":   "https://feeds.reuters.com/reuters/topNews",
    "Hindu":     "https://www.thehindu.com/feeder/default.rss",
    "TOI":       "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    # Add your own sources here:
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "NPR":        "https://feeds.npr.org/1001/rss.xml",
}
```

---

## 🐛 Troubleshooting

### Ollama not running
```bash
# Start Ollama manually
ollama serve

# Or check if it's already running
curl http://localhost:11434
```

### Model not found
```bash
# Pull the model again
ollama pull llama3.2

# List available models
ollama list
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### No articles found
- Try a broader keyword (e.g. `AI` instead of `GPT-5 release date`)
- Check your internet connection (required for RSS/GNews fetching)
- Some RSS feeds may be temporarily unavailable — try switching to GNews API

### JSON parse error in AI response
The `ai_agent.py` includes a 5-layer fallback parser. If you still see errors:
- Lower the number of articles to 1-2 to isolate the issue
- Check Ollama is running: `ollama list`
- Restart Ollama: `ollama serve`
- The article content may be too short or empty for the model to analyze

### GNews API not working
- Verify your key is correctly set in `backend/.env`
- Check you haven't exceeded 100 requests/day (free tier limit)
- The app automatically falls back to RSS feeds if the key is invalid

---

## 📦 Requirements

**`requirements.txt`**
```
fastapi==0.115.0
uvicorn==0.30.6
flask==3.0.3
requests==2.32.3
feedparser==6.0.11
beautifulsoup4==4.12.3
python-dotenv==1.0.1
pydantic==2.8.2
```

---

## 🔄 Quick Reference — All Commands

```bash
# ── SETUP ──────────────────────────────────────────
ollama pull llama3.2                    # Download AI model (once)
pip install -r requirements.txt         # Install Python packages

# ── RUN ────────────────────────────────────────────
cd backend && uvicorn main:app --reload --port 8000    # Terminal 1
cd frontend && python app.py                           # Terminal 2

# ── VERIFY ─────────────────────────────────────────
ollama list                             # Check model is available
curl http://localhost:8000/             # Check FastAPI is running
curl http://localhost:5000/             # Check Flask is running

# ── OLLAMA ─────────────────────────────────────────
ollama serve                            # Start Ollama manually
ollama list                             # List downloaded models
ollama pull llama3.2                    # Download llama3.2
ollama pull phi3                        # Download phi3 (lighter)
ollama run llama3.2 "your prompt"       # Test model in terminal

# ── STOP SERVERS ───────────────────────────────────
Ctrl+C                                  # Stop any running server

# ── PORT CONFLICTS ─────────────────────────────────
lsof -ti:8000 | xargs kill -9          # Free port 8000
lsof -ti:5000 | xargs kill -9          # Free port 5000
```

---

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software, to deal in the Software without restriction, including the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software.
```

---

## 🙏 Acknowledgements

- [Ollama](https://ollama.com) — for making local LLM inference accessible
- [Meta AI](https://ai.meta.com) — for the llama3.2 open-source model
- [FastAPI](https://fastapi.tiangolo.com) — for the excellent Python API framework
- [Flask](https://flask.palletsprojects.com) — for the lightweight web server
- [feedparser](https://feedparser.readthedocs.io) — for robust RSS parsing
- [GNews](https://gnews.io) — for the free news search API
- BBC News, Reuters, The Hindu, Times of India — for free RSS feeds

---

<div align="center">

Built with Python · Flask · FastAPI · Ollama · llama3.2

**NewsAI — 100% local · 100% free · 100% private**

</div>