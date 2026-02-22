# Push to GitHub - Quick Instructions

## Option 1: Run the PowerShell Script (Easiest)

1. Open PowerShell in the `ai_agent_platform` folder
2. Run:
   ```powershell
   .\push_to_github.ps1
   ```
3. When prompted for credentials:
   - **Username**: `Jnabagel`
   - **Password**: Use a **Personal Access Token** (not your GitHub password)

## Option 2: Manual Commands

Copy and paste these commands one by one in PowerShell:

```powershell
# Navigate to project folder
cd "C:\Users\desray\Desktop\Library\Project\ClaudeCode\ai_agent_platform"

# Initialize git (if needed)
git init

# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI Agent Platform with NewsBot and ComplianceSME"

# Add remote
git remote add origin https://github.com/Jnabagel/lark-newsbot.git

# Set main branch
git branch -M main

# Push
git push -u origin main
```

## If You Get Authentication Errors

GitHub requires a **Personal Access Token** instead of a password:

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Name it: `lark-newsbot-push`
4. Select scope: **`repo`** (full control)
5. Click **Generate token**
6. **Copy the token** (you won't see it again!)
7. When git asks for password, paste the token instead

## Verify Success

After pushing, check:
- https://github.com/Jnabagel/lark-newsbot
- Make sure `.env` is **NOT** visible (it should be ignored)
- All other files should be there

## If .env Was Accidentally Pushed

If you see `.env` in your GitHub repo:

```powershell
git rm --cached .env
git commit -m "Remove .env from tracking"
git push
```

Then **immediately rotate all API keys** that were exposed!
