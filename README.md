# AI Agent Platform - MVP

A minimal but production-sensible AI multi-agent system built with Python, FastAPI, and ChromaDB.

## Architecture

- **Main Router**: Routes requests to appropriate agents
- **NewsBot**: Fetches and summarizes daily news, sends to Lark
- **ComplianceSME**: RAG-based compliance knowledge assistant

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `LARK_WEBHOOK_URL`
- Other settings as needed

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

Or:

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```

### Run NewsBot
```
POST /news/run
```

### Query Compliance
```
POST /compliance/query
Body: {"question": "Your question here"}
```

## Project Structure

```
ai_agent_platform/
├── app/              # FastAPI application
├── agents/           # Agent implementations
├── services/         # Core services (LLM, vector store, Lark)
├── ingestion/        # Document loading and chunking
├── config/           # Configuration management
└── logs/             # Application logs
```

## Development Notes

- All agents use dependency injection
- Vector store uses ChromaDB with persistent storage
- Logging is configured to both file and console
- Type hints and docstrings are required
- No hardcoded secrets

## Next Steps

- Implement actual news API integration
- Add document ingestion pipeline
- Set up cron scheduler for daily news runs
- Add authentication/authorization
- Implement proper error handling and retries
