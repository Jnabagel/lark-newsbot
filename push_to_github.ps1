# PowerShell script to push project to GitHub
# Run this in PowerShell: .\push_to_github.ps1

Write-Host "=== Pushing AI Agent Platform to GitHub ===" -ForegroundColor Green

# Navigate to project directory
Set-Location $PSScriptRoot

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
}

# Check git status
Write-Host "`nChecking git status..." -ForegroundColor Yellow
git status

# Verify .env is ignored
Write-Host "`nVerifying .env is ignored..." -ForegroundColor Yellow
if (git ls-files --error-unmatch .env 2>$null) {
    Write-Host "WARNING: .env is tracked! Removing it..." -ForegroundColor Red
    git rm --cached .env
}

# Add all files
Write-Host "`nAdding all files..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "`nCommitting changes..." -ForegroundColor Yellow
git commit -m "Initial commit: AI Agent Platform with NewsBot and ComplianceSME"

# Add remote (if not already added)
Write-Host "`nSetting up remote..." -ForegroundColor Yellow
$remoteExists = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    git remote add origin https://github.com/Jnabagel/lark-newsbot.git
    Write-Host "Remote added: https://github.com/Jnabagel/lark-newsbot.git" -ForegroundColor Green
} else {
    Write-Host "Remote already exists: $remoteExists" -ForegroundColor Yellow
    git remote set-url origin https://github.com/Jnabagel/lark-newsbot.git
    Write-Host "Remote updated to: https://github.com/Jnabagel/lark-newsbot.git" -ForegroundColor Green
}

# Set main branch
Write-Host "`nSetting main branch..." -ForegroundColor Yellow
git branch -M main

# Push to GitHub
Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
Write-Host "You may be prompted for GitHub credentials." -ForegroundColor Cyan
Write-Host "Use your GitHub username and a Personal Access Token (not password)." -ForegroundColor Cyan
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== Success! Project pushed to GitHub ===" -ForegroundColor Green
    Write-Host "Repo: https://github.com/Jnabagel/lark-newsbot" -ForegroundColor Cyan
} else {
    Write-Host "`n=== Push failed. Check error messages above. ===" -ForegroundColor Red
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Authentication: Use Personal Access Token instead of password" -ForegroundColor Yellow
    Write-Host "2. Network: Check your internet connection" -ForegroundColor Yellow
    Write-Host "3. Repo exists: Make sure the repo exists on GitHub" -ForegroundColor Yellow
}
