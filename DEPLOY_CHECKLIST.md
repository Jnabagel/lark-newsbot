# Deployment Checklist - Render + GitHub + Lark

Follow these steps in order to deploy your AI Agent Platform.

---

## ✅ Step 1: Push Code to GitHub

**Status**: [ ] Done

If you haven't pushed yet, run these commands:

```powershell
cd "C:\Users\desray\Desktop\Library\Project\ClaudeCode\ai_agent_platform"

# Check if already committed
git status

# If not committed, do:
git add .
git commit -m "Initial commit: AI Agent Platform"

# Push (use Personal Access Token when prompted)
git push -u origin main
```

**Verify**: Go to https://github.com/jnabagel/lark-newsbot - all files should be there (except `.env`)

---

## ✅ Step 2: Create Render Account

**Status**: [ ] Done

1. Go to [render.com](https://render.com)
2. Sign up (use "Sign up with GitHub" - easiest)
3. Authorize Render to access your GitHub account

---

## ✅ Step 3: Create Web Service on Render

**Status**: [ ] Done

1. In Render Dashboard, click **New +** → **Web Service**
2. **Connect your repository**:
   - Select: `jnabagel/lark-newsbot`
   - If asked for **Root Directory**: `ai_agent_platform` (if your repo root is the parent folder)
3. **Configure service**:
   - **Name**: `lark-newsbot` (or any name you like)
   - **Region**: `Singapore` (closest to Hong Kong) or `Oregon`
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
     ```
   - **Instance Type**: `Free` (or `Starter` for $7/month - no sleep)

4. **Click "Create Web Service"**

---

## ✅ Step 4: Set Environment Variables in Render

**Status**: [ ] Done

In your Render Web Service → **Environment** tab, add these:

### Required Variables:

| Key | Value | Notes |
|-----|-------|-------|
| `LLM_PROVIDER` | `openai` or `anthropic` | Your choice |
| `OPENAI_API_KEY` | `sk-proj-...` | If using OpenAI |
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` | If using Anthropic |
| `ANTHROPIC_BASE_URL` | `https://api.anthropic.com` | Or your custom URL |
| `LARK_WEBHOOK_URL` | `https://open.larksuite.com/...` | Your Lark webhook |
| `LARK_APP_ID` | `cli_a910181c22f89eee` | Your Lark app ID |
| `LARK_APP_SECRET` | `kWIPLp2UwL9kz4w0rBanieUV40SlcRx3` | Your Lark app secret |
| `NEWSDATA_KEY` | `pub_60e857c8306a4b9e9cec71b22fbdaf0f` | Your NewsData.io key |

### Optional Variables:

| Key | Value |
|-----|-------|
| `LOG_LEVEL` | `INFO` |
| `CHROMA_PERSIST_DIR` | `./chroma_db` |
| `EMBEDDING_MODEL` | `text-embedding-ada-002` |

**Important**: Copy values from your local `.env` file, but **never commit `.env` to GitHub!**

---

## ✅ Step 5: Wait for Deployment

**Status**: [ ] Done

1. Render will automatically build and deploy
2. Watch the **Logs** tab for progress
3. Wait until status shows **Live** (green)
4. Your app URL will be: `https://lark-newsbot-xxxx.onrender.com`

**Note**: First deployment takes 5-10 minutes. Subsequent deployments are faster.

---

## ✅ Step 6: Update Lark Webhook URL

**Status**: [ ] Done

1. Go to [Lark Developer Console](https://open.larksuite.com/app)
2. Select your app (App ID: `cli_a910181c22f89eee`)
3. Go to **Event Subscriptions**
4. Update **Request URL** to:
   ```
   https://lark-newsbot-xxxx.onrender.com/lark/webhook
   ```
   (Replace `xxxx` with your actual Render subdomain)
5. **Save** - Lark will verify the URL automatically

---

## ✅ Step 7: Test Everything

**Status**: [ ] Done

### Test 1: Health Check
Open: `https://your-app.onrender.com/health`
Expected: `{"status":"ok"}`

### Test 2: Scheduler Status
Open: `https://your-app.onrender.com/scheduler/status`
Expected: `scheduler_running: true`, `next_run_time` in HKT

### Test 3: Manual NewsBot Run
- Go to: `https://your-app.onrender.com/docs`
- Click **POST /news/run** → **Try it out** → **Execute**
- Check your Lark group for the news summary

### Test 4: Lark Bot Mention
- In your Lark group, type: `@NewsBot news`
- Bot should reply with news summary

---

## ✅ Step 8: (Optional) Keep Free Tier Awake

**Status**: [ ] Done (Optional)

If using **Free tier**, the app sleeps after 15 min inactivity. To ensure 7:30 AM scheduler runs:

### Option A: Use cron-job.org (Free)

1. Go to [cron-job.org](https://cron-job.org)
2. Create account (free)
3. Create new cron job:
   - **URL**: `https://your-app.onrender.com/health`
   - **Schedule**: Every 5 minutes
   - **Save**

This keeps your app awake so scheduler can run at 7:30 AM.

### Option B: Upgrade to Starter ($7/month)

- App never sleeps
- Scheduler always runs on time
- No need for external cron

---

## 🎉 You're Done!

Your AI Agent Platform is now:
- ✅ Deployed on Render
- ✅ Connected to GitHub (auto-deploys on push)
- ✅ Connected to Lark (webhooks + bot)
- ✅ Scheduled to run daily at 7:30 AM HKT
- ✅ Responds to `@NewsBot` mentions

---

## Troubleshooting

### Deployment Fails
- Check **Logs** tab in Render
- Verify all environment variables are set
- Check `requirements.txt` is correct

### Lark Webhook Not Working
- Verify webhook URL is correct
- Check Render logs for errors
- Make sure Lark app permissions are enabled

### Scheduler Not Running
- Free tier: App might be sleeping
- Set up cron job to ping `/health` endpoint
- Or upgrade to paid tier

### Bot Not Responding
- Check Render logs
- Verify `LARK_APP_ID` and `LARK_APP_SECRET` are correct
- Check Lark app permissions

---

## Next Steps After Deployment

1. **Monitor logs**: Check Render logs regularly
2. **Test in production**: Try all features
3. **Set up monitoring**: Consider adding error tracking
4. **Documentation**: Update README with production URLs
