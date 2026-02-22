# Next Steps - Getting Started Guide

## ✅ Step 1: Verify Server is Running

The server should be running at `http://localhost:8000`

**Quick Check:**
- Open browser: http://localhost:8000/health
- Should see: `{"status": "ok"}`

**Or use FastAPI Docs:**
- Open: http://localhost:8000/docs
- Interactive API documentation with "Try it out" buttons

---

## ✅ Step 2: Test the Endpoints

### Option A: Use the Test Script
```bash
python test_endpoints.py
```

### Option B: Manual Testing

**1. Health Check:**
```bash
curl http://localhost:8000/health
```

**2. Test NewsBot:**
```bash
curl -X POST http://localhost:8000/news/run
```

**3. Test ComplianceSME:**
```bash
curl -X POST http://localhost:8000/compliance/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the data privacy requirements?"}'
```

### Option C: Use FastAPI Interactive Docs
1. Go to http://localhost:8000/docs
2. Click on an endpoint
3. Click "Try it out"
4. Fill in parameters and click "Execute"

---

## ✅ Step 3: Set Up Compliance Documents

**ComplianceSME needs documents in the vector store to answer questions.**

Run the setup script:
```bash
python setup_compliance_docs.py
```

This will:
- Create sample compliance documents
- Chunk them into smaller pieces
- Add them to ChromaDB vector store

**After setup, test ComplianceSME:**
```bash
python test_endpoints.py
```

Or query manually:
```bash
curl -X POST http://localhost:8000/compliance/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the data retention requirements?"}'
```

---

## ✅ Step 4: Add Your Own Documents

To add your own compliance documents:

1. **Create a documents folder:**
   ```bash
   mkdir documents
   ```

2. **Add text files (.txt or .md):**
   - Place compliance documents in the `documents/` folder

3. **Create an ingestion script** (or modify `setup_compliance_docs.py`):
   ```python
   from ingestion.document_loader import DocumentLoader
   from ingestion.chunker import Chunker
   from services.vector_store import VectorStore
   
   loader = DocumentLoader()
   chunker = Chunker()
   vector_store = VectorStore()
   
   # Load documents
   docs = loader.load_directory("documents")
   
   # Chunk them
   chunks = chunker.chunk_documents(docs)
   
   # Add to vector store
   vector_store.add_documents(chunks)
   ```

---

## ✅ Step 5: Configure Environment Variables

Make sure your `.env` file has:

```env
# Required for LLM
LLM_PROVIDER=anthropic  # or "openai"
ANTHROPIC_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here

# Required for Lark webhook
LARK_WEBHOOK_URL=your_webhook_url_here

# Optional
LOG_LEVEL=INFO
PORT=8000
```

---

## ✅ Step 6: Monitor Logs

Check application logs:
```bash
# View logs
cat logs/app.log

# Or tail for real-time
tail -f logs/app.log
```

---

## 🚀 Future Enhancements

1. **Real News API Integration**
   - Replace mock headlines in `agents/newsbot.py`
   - Integrate with NewsAPI.org, NewsData.io, or web scraping

2. **Scheduled News Runs**
   - Set up cron job or Windows Task Scheduler
   - Run NewsBot daily at 09:00 HKT

3. **Enhanced Error Handling**
   - Add retries for API calls
   - Better fallback mechanisms

4. **Authentication**
   - Add API key authentication
   - User management

5. **More Agents**
   - Add new agents following the same pattern
   - Extend router to handle new routes

---

## 📝 Quick Reference

**Start Server:**
```bash
python run.py
```

**Test Everything:**
```bash
python test_endpoints.py
```

**Setup Compliance Docs:**
```bash
python setup_compliance_docs.py
```

**API Base URL:**
```
http://localhost:8000
```

**Interactive Docs:**
```
http://localhost:8000/docs
```
