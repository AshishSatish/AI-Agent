# Company Research Assistant

AI-powered system that automates company research and generates comprehensive account plans for sales and business development teams.

---

## Features

- Natural language chat interface
- Multi-source research (25+ web sources via SerpAPI)
- AI-powered data synthesis with conflict detection
- Automated 9-section account plan generation
- Section-specific updates
- Real-time progress via WebSockets
- Voice input support
- Clean Perplexity-inspired UI

---

## Quick Start

### Prerequisites

- Python 3.8+
- [Groq API Key](https://console.groq.com/)
- [SerpAPI Key](https://serpapi.com/)

### Installation

**Windows:**
```bash
setup.bat
# Edit .env with your API keys
venv\Scripts\activate
python run.py
```

**Mac/Linux:**
```bash
chmod +x setup.sh && ./setup.sh
# Edit .env with your API keys
source venv/bin/activate
python run.py
```

Open browser: `http://localhost:8000`

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Add your API keys to .env

# 4. Run
python run.py --mode web
```

---

## Usage

1. **Research**: Click "Quick Research" → Enter company name → Wait for synthesis
2. **Generate Plan**: Click "Generate Plan" after research completes
3. **Update**: Select section → Enter new content → Update
4. **Chat**: Type natural language queries for contextual responses
5. **Voice**: Click microphone icon (Chrome/Edge only)

---

## Architecture

```
User Interface (HTML/JS)
         ↓
    FastAPI Server
         ↓
    ┌────┴────┬────────┬───────────┐
    ↓         ↓        ↓           ↓
  Agent   Researcher Synthesizer  Plan Gen
    ↓         ↓        ↓           ↓
  Groq     SerpAPI   Groq        Groq
```

### Components

- **Agent** (`app/agent.py`): Conversational AI using Groq LLM
- **Researcher** (`app/researcher.py`): Multi-source web search via SerpAPI
- **Synthesizer** (`app/synthesizer.py`): Data consolidation with conflict detection
- **Plan Generator** (`app/account_plan.py`): Structured account plan creation
- **FastAPI Server** (`app/main.py`): REST API + WebSocket server
- **Frontend** (`templates/index.html`): Vanilla JS, Perplexity-style UI

---

## Design Decisions

### Technology Choices

**Groq API (vs OpenAI)**
- 10-20× faster inference
- Free tier: 30 requests/min
- Quality comparable to GPT-4

**SerpAPI (vs Direct Scraping)**
- Legal compliance
- Handles CAPTCHAs automatically
- Structured JSON output

**FastAPI (vs Flask)**
- Native async/await support
- Built-in WebSocket support
- Auto-generated API docs

**In-Memory Sessions (vs Database)**
- Zero latency
- Simple development
- Acceptable for MVP

**Vanilla JS (vs React/Vue)**
- No build step
- Single HTML file
- Sufficient for this UI

**JSON Storage (vs Database)**
- No setup required
- Human-readable
- Git-friendly

### Architecture Patterns

- **Modular Design**: Single responsibility per component
- **Session-Based State**: Maintains conversation context
- **LLM Prompt Engineering**: JSON schemas for structured output
- **Loose Coupling**: Easy to swap implementations

---

## Configuration

Edit `.env`:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_KEY=your_serpapi_key_here

# Optional
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
GROQ_MODEL=llama-3.3-70b-versatile
MAX_RESEARCH_SOURCES=5
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/chat` | POST | Chat message |
| `/api/research` | POST | Research company |
| `/api/generate-plan` | POST | Generate account plan |
| `/api/update-plan` | POST | Update plan section |
| `/api/plans` | GET | List saved plans |
| `/api/plans/{filename}` | GET | Get specific plan |
| `/ws/{session_id}` | WebSocket | Real-time updates |

**Auto-generated docs:** `http://localhost:8000/docs`

---

## Troubleshooting

**Port in use:**
```bash
# Windows: netstat -ano | findstr :8000 && taskkill /PID <PID> /F
# Mac/Linux: lsof -ti:8000 | xargs kill -9
```

**API key errors:** Verify `.env` exists with valid keys, restart server

**Import errors:** `pip install --upgrade -r requirements.txt`

**Voice not working:** Use Chrome/Edge, check microphone permissions

---

## Project Structure

```
AI Agent/
├── app/
│   ├── agent.py              # Conversational AI
│   ├── researcher.py         # Web research
│   ├── synthesizer.py        # Data synthesis
│   ├── account_plan.py       # Plan generation
│   ├── main.py               # FastAPI server
│   ├── config.py             # Configuration
│   └── voice.py              # Voice I/O
├── templates/
│   └── index.html            # Web UI
├── data/                     # Saved plans (JSON)
├── .env                      # API keys (not in repo)
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Dependencies
├── run.py                    # Entry point
└── README.md                 # This file
```

---

## Performance

- Chat: 1-2 seconds
- Research: 10-30 seconds (5 sequential queries)
- Plan Generation: 5-10 seconds

**Optimization ideas:** Parallel queries, caching, database for production

---

## Cost Estimate

**Development (Free):**
- Groq: 30 req/min
- SerpAPI: 100 searches/month

**Production (~$60-100/month):**
- Groq: ~$0.10 per 1M tokens
- SerpAPI: $50/month
- Hosting: $10-50/month

---

## License

MIT License - Free for personal and commercial use.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Groq](https://groq.com/) - LLM inference
- [SerpAPI](https://serpapi.com/) - Web search
- [Perplexity](https://www.perplexity.ai/) - UI inspiration

---

For detailed technical documentation, see `TECHNICAL_DOCUMENTATION.txt`
