# NewsBot Status & Configuration Guide

## Current Status

### ✅ What's Working

1. **Code Structure**: Complete and ready
2. **LLM Integration**: Uses OpenAI/Anthropic for summarization
3. **Lark Integration**: Code is ready, sends markdown messages
4. **API Endpoint**: `/news/run` endpoint is functional
5. **Error Handling**: Fallback mechanisms in place

### ⚠️ What Needs Configuration

1. **Lark Webhook URL**: Not configured yet
   - Current: `LARK_WEBHOOK_URL=your_lark_webhook_url_here`
   - **Action**: Get webhook URL from Lark and update `.env`

2. **News Sources**: Currently using **MOCK DATA**
   - Real news APIs are implemented but need API keys
   - Falls back to mock data if APIs unavailable

---

## News Sources Configuration

### Option 1: Use Real News APIs (Recommended)

**NewsAPI.org** (Free tier available):
1. Sign up at https://newsapi.org/
2. Get your API key
3. Add to `.env`:
   ```env
   NEWSAPI_KEY=your_newsapi_key_here
   ```

**NewsData.io** (Free tier available):
1. Sign up at https://newsdata.io/
2. Get your API key
3. Add to `.env`:
   ```env
   NEWSDATA_KEY=your_newsdata_key_here
   ```

**Both APIs support:**
- Reuters, BBC, AP, SCMP, HKFP sources
- Hong Kong regional news
- Free tiers available (with rate limits)

### Option 2: Use Mock Data (Current)

If no API keys are configured, NewsBot will use mock headlines. This is fine for testing but not for production.

---

## Lark Webhook Setup

### Steps to Get Lark Webhook URL:

1. **Open Lark/Feishu**
2. **Go to your group/chat** where you want news sent
3. **Add a Bot/Custom Bot**:
   - Group Settings → Bots → Add Bot
   - Or use Lark Open Platform
4. **Get Webhook URL**:
   - Copy the webhook URL (format: `https://open.feishu.cn/open-apis/bot/v2/hook/...`)
5. **Add to `.env`**:
   ```env
   LARK_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID
   ```

### Testing Lark Integration

After configuring webhook URL, test it:
```bash
python test_endpoints.py
```

Or manually:
```bash
curl -X POST http://localhost:8000/news/run
```

Check your Lark group/chat for the message.

---

## Testing NewsBot

### Test with Mock Data (No API Keys Needed)

```bash
# Start server
python run.py

# In another terminal, test NewsBot
python test_endpoints.py
```

**Expected Behavior:**
- ✅ Fetches mock headlines
- ✅ Generates summary using LLM
- ⚠️ Lark send will fail (if webhook not configured)
- ✅ API returns summary in response

### Test with Real News (Requires API Keys)

1. **Add API keys to `.env`**:
   ```env
   NEWSAPI_KEY=your_key_here
   # OR
   NEWSDATA_KEY=your_key_here
   ```

2. **Restart server**:
   ```bash
   python run.py
   ```

3. **Test**:
   ```bash
   python test_endpoints.py
   ```

**Expected Behavior:**
- ✅ Fetches real headlines from APIs
- ✅ Generates summary using LLM
- ✅ Sends to Lark (if webhook configured)
- ✅ API returns summary in response

---

## Current Implementation Details

### News Fetching Flow

```
1. NewsBot.run() called
   ↓
2. _fetch_news_headlines()
   ├─→ Try NewsAPI.org (if key configured)
   ├─→ Try NewsData.io (if key configured)
   └─→ Fallback to mock data (if APIs fail/unavailable)
   ↓
3. _summarize_headlines()
   └─→ Uses LLM to generate markdown summary
   ↓
4. Send to Lark
   └─→ lark_client.send_markdown()
   ↓
5. Return result
```

### Mock Data Sources

Current mock headlines simulate:
- Reuters
- BBC
- AP (Associated Press)
- SCMP (South China Morning Post)
- HKFP (Hong Kong Free Press)

---

## Next Steps

1. **Get Lark Webhook URL** and add to `.env`
2. **Get News API Key** (optional but recommended):
   - Sign up for NewsAPI.org or NewsData.io
   - Add key to `.env`
3. **Test end-to-end**:
   ```bash
   python test_endpoints.py
   ```
4. **Check logs**:
   ```bash
   cat logs/app.log
   ```

---

## Troubleshooting

### "LARK_WEBHOOK_URL is required" Error

**Solution**: Add webhook URL to `.env` file

### NewsBot Returns Mock Data

**Possible Causes:**
- No API keys configured → Expected behavior
- API keys invalid → Check logs for errors
- API rate limit exceeded → Wait or upgrade plan

**Solution**: Check `logs/app.log` for details

### Lark Message Not Received

**Check:**
1. Webhook URL is correct
2. Bot has permission to send messages
3. Check logs for Lark API errors
4. Test webhook URL manually with curl

---

## Summary

| Component | Status | Action Needed |
|-----------|--------|---------------|
| Code | ✅ Ready | None |
| LLM | ✅ Ready | Configure API key in `.env` |
| Lark Integration | ✅ Ready | Add webhook URL to `.env` |
| News APIs | ✅ Ready | Add API keys to `.env` (optional) |
| Mock Data | ✅ Working | None (fallback) |

**Current State**: Ready for testing with mock data. Configure API keys for production use.
