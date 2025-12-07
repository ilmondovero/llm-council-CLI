# LLM Council

![LLM Council](header.jpg)

🇬🇧 English | [🇮🇹 Italiano](README_IT.md)

A local, CLI-based multi-model AI deliberation system that brings together Google Gemini, OpenAI Codex, and Anthropic Claude to collaboratively answer your questions through a structured 3-stage process.

## Overview

Instead of asking a single LLM for an answer, LLM Council orchestrates a collaborative deliberation process across multiple AI models. The system implements a structured decision-making framework:

### The 3-Stage Process

#### Stage 1: Individual Responses
Each council member (Gemini, Codex, Claude) independently analyzes your question and provides their own response. This ensures diverse perspectives without groupthink or bias.

#### Stage 2: Anonymized Peer Review
The responses are anonymized (labeled as Response A, Response B, Response C) and redistributed to all council members. Each model reviews and ranks all responses based on accuracy, insight, and completeness - without knowing which model produced which answer.

#### Stage 3: Chairman Synthesis
The designated Chairman model (by default, Gemini) reviews all individual responses and peer rankings to synthesize a final, comprehensive answer that represents the council's collective wisdom.

## Key Features

- **Multi-Model Intelligence**: Harnesses the strengths of Google Gemini, OpenAI Codex (GPT/o-series), and Anthropic Claude
- **No API Keys Required**: Uses local CLI tools with your existing subscriptions - no OpenRouter or additional API keys needed
- **Privacy-First**: All processing happens locally via CLI subprocesses
- **Transparent Process**: See all individual responses, peer rankings, and the synthesis process
- **Conversation History**: Automatically saved and retrievable
- **Modern UI**: Clean React frontend with real-time streaming responses

## Prerequisites

Before running LLM Council, you need to install and authenticate three CLI tools:

- **Gemini CLI** (Google)
- **Codex CLI** (OpenAI)
- **Claude CLI** (Anthropic)

See the complete installation guide: [docs/INSTALL_CLI.md](docs/INSTALL_CLI.md)

## Quick Start

### 1. Install Dependencies

The project uses Python 3.10+ for the backend and Node.js for the frontend.

**Install Python dependencies:**
```bash
pip install fastapi uvicorn httpx pydantic
```

Or using uv (recommended):
```bash
uv sync
```

**Install frontend dependencies:**
```bash
cd frontend
npm install
cd ..
```

### 2. Start the Application

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

This will:
- Start the FastAPI backend on http://localhost:8001
- Start the React frontend on http://localhost:5173
- Automatically open your browser

### 3. Start Asking Questions

Navigate to http://localhost:5173 and start a conversation. Watch as the three models independently respond, review each other's work, and produce a synthesized final answer.

## Usage

### Starting a Conversation

1. Click "New Conversation" in the sidebar
2. Type your question in the input field
3. Press Enter or click Send

### Viewing Responses

The interface shows all three stages:

- **Stage 1 Tabs**: Click through individual responses from Gemini, Codex, and Claude
- **Stage 2 Rankings**: See how each model ranked the others (with aggregate scores)
- **Stage 3 Final Answer**: The Chairman's synthesized response

### Managing Conversations

- Click any conversation in the sidebar to view history
- Conversations are automatically titled based on your first message
- All data is stored locally in `data/conversations/`

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```bash
# API server configuration
PORT=8001                                    # Backend port (default: 8001)
CORS_ORIGINS=http://localhost:5173          # Allowed CORS origins

# Council configuration (advanced - see backend/config.py instead)
```

### Council Configuration

Edit `backend/config.py` to customize the council:

```python
# Council members - CLI identifiers
COUNCIL_MODELS = [
    "gemini",   # Google Gemini via Gemini CLI
    "codex",    # OpenAI GPT via Codex CLI
    "claude",   # Anthropic Claude via Claude CLI
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "gemini"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
```

### CLI Configuration

The system invokes CLIs via subprocess. Each CLI must be:
1. Installed and available in your PATH
2. Authenticated with valid credentials
3. Working with a test prompt

Verify your setup:
```bash
# Test each CLI
echo "Hello" | gemini
codex exec "What is 2+2?"
echo "Hello" | claude -p
```

## API Reference

The backend exposes a RESTful API on port 8001:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/conversations` | GET | List all conversations (metadata) |
| `/api/conversations` | POST | Create new conversation |
| `/api/conversations/{id}` | GET | Get conversation with all messages |
| `/api/conversations/{id}/message` | POST | Send message (full response) |
| `/api/conversations/{id}/message/stream` | POST | Send message (SSE streaming) |

### Example: Send a Message

```bash
curl -X POST http://localhost:8001/api/conversations/{id}/message \
  -H "Content-Type: application/json" \
  -d '{"content": "What is quantum computing?"}'
```

Response includes all three stages:
```json
{
  "stage1": [
    {"model": "gemini", "response": "..."},
    {"model": "codex", "response": "..."},
    {"model": "claude", "response": "..."}
  ],
  "stage2": [
    {"model": "gemini", "ranking": "...", "parsed_ranking": ["Response A", "Response C", "Response B"]},
    ...
  ],
  "stage3": {
    "model": "gemini",
    "response": "..."
  },
  "metadata": {
    "label_to_model": {"Response A": "gemini", ...},
    "aggregate_rankings": [...]
  }
}
```

## Tech Stack

**Backend:**
- FastAPI (Python 3.10+)
- Async subprocess execution for CLI invocation
- JSON file storage for conversations
- Server-Sent Events (SSE) for streaming

**Frontend:**
- React 19 with Hooks
- Vite for build tooling
- react-markdown for response rendering
- CSS3 for styling

**CLI Integration:**
- Gemini CLI: `echo "prompt" | gemini`
- Codex CLI: `codex exec "prompt"`
- Claude CLI: `echo "prompt" | claude -p`

## Project Structure

```
llm-council-master/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── council.py        # 3-stage orchestration logic
│   ├── cli_bridge.py     # CLI subprocess execution
│   ├── config.py         # Configuration
│   └── storage.py        # JSON file storage
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main application
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx  # Main chat UI
│   │   │   ├── Sidebar.jsx        # Conversation list
│   │   │   ├── Stage1.jsx         # Individual responses
│   │   │   ├── Stage2.jsx         # Rankings
│   │   │   └── Stage3.jsx         # Final synthesis
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── INSTALL_CLI.md    # CLI installation guide
│   ├── ARCHITECTURE.md   # System architecture
│   └── PLAN_TDD.md       # Development plans
├── data/
│   └── conversations/    # Stored conversations (JSON)
├── start.bat             # Windows startup script
├── start.sh              # Unix startup script
├── pyproject.toml        # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Install dependencies: `pip install fastapi uvicorn httpx pydantic`
- Check port 8001 is available: `netstat -an | grep 8001`

### Frontend won't start
- Check Node.js version: `node --version` (need 14+)
- Install dependencies: `cd frontend && npm install`
- Check port 5173 is available

### CLI not found errors
- Verify CLI installation: `which gemini` / `which codex` / `which claude`
- Ensure CLIs are in your PATH
- See [docs/INSTALL_CLI.md](docs/INSTALL_CLI.md) for installation help

### Models timeout
- Default timeout is 120 seconds per CLI call
- Check your network connection
- Verify CLI authentication: run test commands manually
- Increase timeout in `backend/cli_bridge.py` if needed

### Empty or error responses
- Check CLI authentication status
- Run CLIs manually to verify they work: `echo "test" | gemini`
- Check backend logs for detailed error messages
- Verify you have active subscriptions for all three services

## Contributing

This project is provided as-is for inspiration and learning. Feel free to fork and modify it for your needs. The code is designed to be readable and hackable - ask your favorite LLM to help you customize it!

### Development

Run backend in development mode:
```bash
python -m backend.main
```

Run frontend in development mode:
```bash
cd frontend
npm run dev
```

Run tests:
```bash
# Backend tests
python -m pytest backend/tests/

# Test CLIs manually
python -m backend.tests.test_cli_bridge
```

## License

MIT License - see the code and use it however you like. This project was created as a weekend hack to explore multi-model AI collaboration.

## Acknowledgments

- Original concept inspired by the need to compare multiple LLMs side-by-side
- Built with inspiration from Andrej Karpathy's approach to reading books with LLMs
- Special thanks to the teams at Google, OpenAI, and Anthropic for their excellent CLI tools

---

**Note**: This is a local development tool. For production use, consider adding authentication, rate limiting, and proper error handling.
