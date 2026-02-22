# Lark Bot Setup Guide

## Overview

NewsBot can now respond to on-demand requests in Lark when users mention it with commands like:
- `@NewsBot news`
- `@NewsBot summary`
- `@NewsBot news business`
- `@NewsBot news technology`

## Features

✅ **Mention-based triggers**: Users mention `@NewsBot` with commands  
✅ **Full summary**: Sends complete markdown summary  
✅ **Same thread replies**: Replies in the same chat/group  
✅ **No rate limits**: Unlimited requests  
✅ **Simple errors**: User-friendly error messages  
✅ **Category filtering**: Filter by business, technology, world, etc.

## Setup Steps

### 1. Create Lark Bot App

1. Go to [Lark Developer Console](https://open.larksuite.com/app)
2. Create a new app or use existing app
3. Note your **App ID** and **App Secret**

### 2. Configure Bot Permissions

In your Lark app settings, enable:

**Required Permissions:**
- `im:message` - Send and receive messages
- `im:message:group:readonly` - Read group messages
- `im:message:group:send` - Send messages to groups

**Event Subscriptions:**
- Enable `im.message.receive_v1` - Receive message events

### 3. Configure Webhook URL

1. In Lark Developer Console → **Event Subscriptions**
2. Set **Request URL** to:
   ```
   https://your-domain.com/lark/webhook
   ```
   Or for local testing with ngrok:
   ```
   https://your-ngrok-url.ngrok.io/lark/webhook
   ```

3. **Encryption**: You can use "No Encryption" for testing, or configure encryption key

4. **Save** the configuration

### 4. Add Bot to Group/Chat

1. Go to your Lark group/chat
2. Add the bot as a member
3. Make sure bot has permission to send messages

### 5. Update Environment Variables

Add to your `.env` file:

```env
LARK_APP_ID=your_app_id_here
LARK_APP_SECRET=your_app_secret_here
```

### 6. Restart Server

```bash
python run.py
```

## Testing Locally

### Option 1: Use ngrok (Recommended)

1. **Install ngrok**: https://ngrok.com/

2. **Start your server**:
   ```bash
   python run.py
   ```

3. **Start ngrok tunnel**:
   ```bash
   ngrok http 8000
   ```

4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

5. **Update Lark webhook URL**:
   ```
   https://abc123.ngrok.io/lark/webhook
   ```

6. **Test in Lark**: Mention `@NewsBot news` in your group

### Option 2: Deploy to Server

Deploy your FastAPI app to a server with a public URL and configure the webhook.

## Usage Examples

### Basic Commands

```
@NewsBot news
@NewsBot summary
@NewsBot headlines
```

### Category Filtering

```
@NewsBot news business
@NewsBot news technology
@NewsBot news world
@NewsBot news sports
@NewsBot news entertainment
@NewsBot news health
@NewsBot news science
```

### Supported Categories

- `business` - Business, finance, economy, market news
- `technology` - Tech, AI, software news
- `world` - World, global, international news
- `sports` - Sports news
- `entertainment` - Entertainment news
- `health` - Health, medical news
- `science` - Science news

## How It Works

1. **User mentions bot**: `@NewsBot news business`
2. **Lark sends event** to `/lark/webhook`
3. **Bot parses message**: Extracts command and category
4. **Bot sends "processing" message**: "Fetching latest news summary..."
5. **NewsBot runs**: Fetches news (with category filter if specified)
6. **Bot sends summary**: Full markdown summary in same thread

## Troubleshooting

### Bot Not Responding

1. **Check webhook URL**: Verify it's accessible
2. **Check logs**: `logs/app.log` for errors
3. **Verify bot permissions**: Bot needs message read/send permissions
4. **Check app credentials**: Verify `LARK_APP_ID` and `LARK_APP_SECRET` are correct

### URL Verification Failed

When setting up webhook, Lark sends a verification challenge. The endpoint handles this automatically. If it fails:

1. Check server logs
2. Verify webhook URL is accessible
3. Make sure endpoint returns `{"challenge": "..."}`

### Bot Can't Send Messages

1. **Check permissions**: Bot needs `im:message:group:send`
2. **Verify bot is in group**: Bot must be added to the group/chat
3. **Check access token**: Verify app credentials are correct

### Category Not Working

- Category filtering uses NewsData.io API
- If category not supported, falls back to general news
- Check logs for API errors

## API Endpoints

### Webhook Endpoint
```
POST /lark/webhook
```
Receives Lark events and handles message processing.

### Test Endpoint
You can still manually trigger NewsBot:
```
POST /news/run
```

## Security Notes

- Webhook endpoint should be HTTPS in production
- Consider adding webhook signature verification
- Keep `LARK_APP_SECRET` secure
- Use environment variables, never commit secrets

## Summary

✅ **Setup**: Create Lark app, configure webhook, add credentials  
✅ **Usage**: Mention `@NewsBot news` in Lark  
✅ **Features**: Full summaries, category filtering, same-thread replies  
✅ **Testing**: Use ngrok for local development  

The bot will automatically respond to mentions and fetch news summaries on-demand!
