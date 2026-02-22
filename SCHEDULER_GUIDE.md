# NewsBot Scheduler Guide

## Overview

NewsBot is now configured to automatically run **every day at 7:30 AM Hong Kong Time (HKT)** without any manual intervention.

## How It Works

1. **Automatic Startup**: When you start the FastAPI server, the scheduler automatically starts
2. **Daily Execution**: NewsBot runs at 7:30 AM HKT every day
3. **Background Process**: Runs in the background, doesn't block the API server
4. **Automatic News Fetching**: Fetches real news from NewsData.io
5. **Lark Integration**: Automatically sends the summary to your Lark group

## Setup

### 1. Install Dependencies

Make sure you have the new scheduler dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- `apscheduler` - For job scheduling
- `pytz` - For timezone handling

### 2. Start the Server

```bash
python run.py
```

The scheduler will automatically start when the server starts.

### 3. Verify Scheduler Status

Check if the scheduler is running:

**Via API:**
```bash
curl http://localhost:8000/scheduler/status
```

**Via Browser:**
Open: http://localhost:8000/scheduler/status

**Response:**
```json
{
  "scheduler_running": true,
  "next_run_time": "2026-02-23T07:30:00+08:00",
  "timezone": "Asia/Hong_Kong"
}
```

## Important Notes

### Server Must Be Running

⚠️ **The server must be running 24/7 for the scheduler to work.**

The scheduler runs as part of the FastAPI application. If you stop the server, the scheduler stops too.

### Options for 24/7 Operation

**Option 1: Keep Terminal Open**
- Run `python run.py` in a terminal
- Keep the terminal open and the server running

**Option 2: Run as Background Service (Windows)**
```bash
# Run in background
pythonw run.py
```

**Option 3: Use Windows Task Scheduler**
- Create a task to run `python run.py` at system startup
- Set it to run in background

**Option 4: Use PM2 (if you have Node.js)**
```bash
npm install -g pm2
pm2 start run.py --interpreter python --name newsbot
pm2 save
pm2 startup
```

**Option 5: Docker (Production)**
- Containerize the app and run it as a service

### Timezone

The scheduler uses **Asia/Hong_Kong** timezone (HKT = UTC+8).

- **7:30 AM HKT** = 11:30 PM UTC (previous day)
- Automatically handles daylight saving time (HKT doesn't observe DST)

## Testing the Scheduler

### Test Immediately (Without Waiting)

You can manually trigger NewsBot anytime:

```bash
curl -X POST http://localhost:8000/news/run
```

### Verify Next Run Time

Check when the next automatic run will happen:

```bash
curl http://localhost:8000/scheduler/status
```

### Check Logs

Monitor scheduler activity:

```bash
# View logs
cat logs/app.log

# Or tail for real-time
tail -f logs/app.log
```

Look for:
- `"Scheduler started. Next NewsBot run: ..."`
- `"Scheduled NewsBot run triggered"`
- `"Scheduled NewsBot completed successfully"`

## Manual Override

You can still manually trigger NewsBot anytime:

```bash
# Via API
curl -X POST http://localhost:8000/news/run

# Via Browser
http://localhost:8000/docs → POST /news/run → Try it out
```

Manual runs don't affect the scheduled runs.

## Troubleshooting

### Scheduler Not Running

**Check status:**
```bash
curl http://localhost:8000/scheduler/status
```

If `scheduler_running` is `false`, restart the server.

### NewsBot Not Running at Scheduled Time

1. **Check server is running**: The server must be active
2. **Check logs**: `logs/app.log` for errors
3. **Verify timezone**: Make sure your system clock is correct
4. **Check API keys**: NewsData.io and Lark webhook must be configured

### Change Schedule Time

Edit `services/scheduler.py`:

```python
# Change hour and minute
trigger=CronTrigger(hour=9, minute=0, timezone=pytz.timezone('Asia/Hong_Kong'))
```

Then restart the server.

## Summary

✅ **Automatic**: Runs daily at 7:30 AM HKT  
✅ **No Manual Prompt**: Completely automatic  
✅ **Real News**: Fetches from NewsData.io  
✅ **Lark Integration**: Sends to your Lark group  
✅ **Status Endpoint**: Check `/scheduler/status`  

**Remember**: Keep the server running 24/7 for automatic execution!
