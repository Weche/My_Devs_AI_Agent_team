# Cleanup Old Apps and Deploy My_Devs_AI_Agent_team
# This script will safely remove old apps and deploy the new multi-agent system

$ErrorActionPreference = "Stop"
$env:PATH = "$env:PATH;C:\Users\Christian Orquera\.fly\bin"

Write-Host "=== Fly.io Cleanup & Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Review what will be deleted
Write-Host "Current Fly.io Apps:" -ForegroundColor Yellow
flyctl apps list
Write-Host ""

Write-Host "⚠️  WARNING: This will DELETE the following apps:" -ForegroundColor Red
Write-Host "   1. agents101-app" -ForegroundColor Red
Write-Host "   2. pharmacy-finder-chile" -ForegroundColor Red
Write-Host ""
Write-Host "Are you sure you want to continue? (y/n)" -ForegroundColor Yellow
$confirm = Read-Host

if ($confirm -ne 'y') {
    Write-Host "Aborted. No changes made." -ForegroundColor Green
    exit
}

Write-Host ""
Write-Host "Step 1: Destroying agents101-app..." -ForegroundColor Yellow
try {
    flyctl apps destroy agents101-app --yes
    Write-Host "✅ agents101-app destroyed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Failed to destroy agents101-app: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Destroying pharmacy-finder-chile..." -ForegroundColor Yellow
try {
    flyctl apps destroy pharmacy-finder-chile --yes
    Write-Host "✅ pharmacy-finder-chile destroyed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Failed to destroy pharmacy-finder-chile: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Verifying cleanup..." -ForegroundColor Yellow
flyctl apps list

Write-Host ""
Write-Host "=== Cleanup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Choose deployment option (1, 2, or 3)"
Write-Host "2. I'll create the Dockerfiles"
Write-Host "3. Deploy My_Devs_AI_Agent_team"
Write-Host ""

Pause
