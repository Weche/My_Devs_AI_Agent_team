# Fly.io Setup Script for My_Devs_AI_Agent_team
# Run this to check your current Fly.io deployments and prepare for deployment

Write-Host "=== Fly.io Setup ===" -ForegroundColor Cyan
Write-Host ""

# Add flyctl to PATH for this session
$env:PATH = "$env:PATH;C:\Users\Christian Orquera\.fly\bin"

# Check if logged in
Write-Host "Step 1: Logging in to Fly.io..." -ForegroundColor Yellow
flyctl auth login

Write-Host ""
Write-Host "Step 2: Checking existing apps..." -ForegroundColor Yellow
flyctl apps list

Write-Host ""
Write-Host "Step 3: Checking organizations..." -ForegroundColor Yellow
flyctl orgs list

Write-Host ""
Write-Host "=== Current Status ===" -ForegroundColor Cyan
Write-Host "✅ Fly CLI installed at: C:\Users\Christian Orquera\.fly\bin\flyctl.exe"
Write-Host "✅ Logged in to Fly.io"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Review your existing apps above"
Write-Host "2. Check DEPLOYMENT_GUIDE.md for deployment options"
Write-Host "3. Run: flyctl status -a <app-name> to check specific apps"
Write-Host ""
Write-Host "To deploy this project:" -ForegroundColor Green
Write-Host "- Option 1 (Simple): Single monolithic app (~$5-10/month)"
Write-Host "- Option 2 (Recommended): 2 apps - Albedo + Dev Agents (~$13-20/month)"
Write-Host "- Option 3 (Advanced): 5 microservices (~$40-60/month)"
Write-Host ""

Pause
