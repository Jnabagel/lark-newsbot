# Deploy AI Agent Platform to Render

Step-by-step guide to deploy your FastAPI app to Render so Lark webhooks and the daily scheduler work.

---

## 1. Push code to GitHub

1. Create a repo on GitHub (e.g. `ai-agent-platform`).
2. Push your project (only the `ai_agent_platform` folder or the whole project):

```bash
cd ai_agent_platform
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-agent-platform.git
git push -u origin main
```

If the repo is the **parent** folder (e.g. `ClaudeCode`), ensure Render is set to use the subfolder (see step 3).

---

## 2. Create a Render account

1. Go to [render.com](https://render.com) and sign up (GitHub login is easiest).
2. Connect your GitHub account so Render can access your repo.

---

## 3. Create a Web Service

1. In Render Dashboard click **New +** → **Web Service**.
2. Connect your GitHub repo (the one that contains `ai_agent_platform`).
3. Configure:
   - **Name**: e.g. `ai-agent-platform`
   - **Region**: e.g. Singapore (closer to HK) or Oregon
   - **Branch**: `main`
   - **Root Directory** (if repo root is parent folder): `ai_agent_platform`
   - **Runtime**: **Python 3**
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     python -m gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
     ```

4. **Instance type**: Free (or paid if you want no sleep).

---

## 4. Set environment variables

In your Render Web Service → **Environment** tab, add these (use your real values):

**Required**

| Key | Value |
|-----|--------|
| `LLM_PROVIDER` | `openai` or `anthropic` |
| `OPENAI_API_KEY` | Your OpenAI key |
| or `ANTHROPIC_API_KEY` | Your Anthropic key |
| `LARK_WEBHOOK_URL` | Your Lark webhook URL |
| `LARK_APP_ID` | Your Lark app ID |
| `LARK_APP_SECRET` | Your Lark app secret |
| `NEWSDATA_KEY` | Your NewsData.io key |

**Optional**

| Key | Value |
|-----|--------|
| `ANTHROPIC_BASE_URL` | Only if using custom Anthropic endpoint |
| `LOG_LEVEL` | `INFO` |
| `CHROMA_PERSIST_DIR` | `./chroma_db` (default; free tier disk is ephemeral) |

Do **not** commit `.env` to the repo; set everything in Render’s Environment.

---

## 5. Deploy

1. Click **Create Web Service**.
2. Render will build and deploy. Wait until status is **Live**.
3. Your app URL will be like: `https://ai-agent-platform-xxxx.onrender.com`

---

## 6. Point Lark to your Render URL

1. Open [Lark Developer Console](https://open.larksuite.com/app) → your app → Event Subscriptions.
2. Set **Request URL** to:
   ```
   https://ai-agent-platform-xxxx.onrender.com/lark/webhook
   ```
   (Use your actual Render URL.)
3. Save. Lark will send a verification request; your app should respond and verification should succeed.

---

## 7. Free tier: app sleeps after 15 minutes

On the free plan the service sleeps after ~15 minutes of no traffic. When it’s asleep:

- **Lark webhook**: The first request after sleep may time out while Render wakes the app (often 30–60 seconds). You can retry from Lark or send the message again.
- **Daily 7:30 AM run**: The scheduler only runs while the app is awake. If the app is asleep at 7:30 AM, that run will be missed.

**Ways to keep the 7:30 AM run reliable:**

1. **Use a cron service to wake the app** (recommended on free tier):
   - Use [cron-job.org](https://cron-job.org) or [Uptime Robot](https://uptimerobot.com).
   - Schedule a GET request every 5–10 minutes (or at least before 7:30 AM) to:
     ```
     https://ai-agent-platform-xxxx.onrender.com/health
     ```
   - This keeps the service awake so the in-app scheduler can run at 7:30 AM.

2. **Or upgrade to a paid plan** so the service doesn’t sleep and the scheduler always runs.

---

## 8. Verify after deploy

1. **Health**:  
   Open: `https://your-app.onrender.com/health`  
   Expected: `{"status":"ok"}`

2. **Scheduler**:  
   Open: `https://your-app.onrender.com/scheduler/status`  
   Expected: `scheduler_running: true`, `next_run_time` in HKT.

3. **Manual news run**:  
   `POST` to `https://your-app.onrender.com/news/run` (e.g. from browser `/docs` or curl).

4. **Lark**:  
   In your Lark group, send: `@NewsBot news`  
   You should get a reply (after possible cold start on free tier).

---

## 9. ChromaDB / disk on free tier

On Render’s free tier the filesystem is **ephemeral**: it’s reset on each deploy or restart. So:

- **ComplianceSME** and ChromaDB will lose stored documents after a new deploy or restart.
- For a persistent vector DB you’d later use an external store (e.g. hosted ChromaDB, Pinecone) or a DB that fits your stack.

For NewsBot and Lark-only use, this is fine without changing anything.

---

## Quick checklist

- [ ] Code on GitHub
- [ ] Render Web Service created (Python, correct root dir)
- [ ] Build: `pip install -r requirements.txt`
- [ ] Start: `python -m gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT`
- [ ] All env vars set in Render (no `.env` in repo)
- [ ] Deploy successful, app **Live**
- [ ] Lark Request URL = `https://your-render-url/lark/webhook`
- [ ] (Optional) Cron or uptime ping to `/health` so 7:30 AM run works on free tier

After this, “next steps” are: use the app in Lark and, if you want reliable 7:30 AM runs on free tier, set up the health-check cron.
