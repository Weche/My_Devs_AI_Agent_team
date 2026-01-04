# Suspend Old Apps (Safer Alternative)
# This suspends apps instead of deleting them
# You can resume them later if needed

$ErrorActionPreference = "Stop"
$env:PATH = "$env:PATH;C:\Users\Christian Orquera\.fly\bin"

Write-Host "=== Suspend Old Fly.io Apps ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "This will SUSPEND (not delete) your old apps:" -ForegroundColor Yellow
Write-Host "   1. agents101-app"
Write-Host "   2. pharmacy-finder-chile"
Write-Host ""
Write-Host "Suspended apps don't run and don't cost money." -ForegroundColor Green
Write-Host "You can resume them later with: flyctl scale count 1 -a <app-name>" -ForegroundColor Green
Write-Host ""
Write-Host "Continue? (y/n)" -ForegroundColor Yellow
$confirm = Read-Host

if ($confirm -ne 'y') {
    Write-Host "Aborted." -ForegroundColor Green
    exit
}

Write-Host ""
Write-Host "Suspending agents101-app..." -ForegroundColor Yellow
flyctl scale count 0 -a agents101-app
Write-Host "✅ agents101-app suspended" -ForegroundColor Green

Write-Host ""
Write-Host "Suspending pharmacy-finder-chile..." -ForegroundColor Yellow
flyctl scale count 0 -a pharmacy-finder-chile
Write-Host "✅ pharmacy-finder-chile suspended" -ForegroundColor Green

Write-Host ""
Write-Host "=== Apps Suspended Successfully ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your apps are now suspended and won't cost anything." -ForegroundColor Cyan
Write-Host "Ready to deploy My_Devs_AI_Agent_team!" -ForegroundColor Cyan
Write-Host ""

flyctl apps list

Pause
