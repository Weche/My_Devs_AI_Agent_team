# Deploy Albedo AI Team to Fly.io
# This script safely deploys WITHOUT exposing .env secrets

$ErrorActionPreference = "Stop"
$env:PATH = "$env:PATH;C:\Users\Christian Orquera\.fly\bin"

Write-Host "=== Deploy Albedo AI Team to Fly.io ===" -ForegroundColor Cyan
Write-Host ""

# Load .env file to get secrets (but don't include in Docker image!)
Write-Host "Step 1: Loading secrets from .env file..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please ensure .env exists in the project root with all API keys." -ForegroundColor Red
    exit 1
}

# Parse .env file
$envVars = @{}
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.+)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

Write-Host "✅ Loaded secrets from .env" -ForegroundColor Green
Write-Host "   Found $($envVars.Count) environment variables" -ForegroundColor Gray
Write-Host ""

# Step 2: Create Fly app
Write-Host "Step 2: Creating Fly app..." -ForegroundColor Yellow

$appExists = flyctl apps list 2>&1 | Select-String "albedo-ai-team"

if ($appExists) {
    Write-Host "ℹ️  App 'albedo-ai-team' already exists, skipping creation" -ForegroundColor Gray
} else {
    Write-Host "Creating new app 'albedo-ai-team'..." -ForegroundColor Gray
    flyctl apps create albedo-ai-team --org personal
    Write-Host "✅ App created" -ForegroundColor Green
}

Write-Host ""

# Step 3: Create volume for database
Write-Host "Step 3: Creating persistent volume for database..." -ForegroundColor Yellow

$volumeExists = flyctl volumes list -a albedo-ai-team 2>&1 | Select-String "albedo_data"

if ($volumeExists) {
    Write-Host "ℹ️  Volume 'albedo_data' already exists, skipping creation" -ForegroundColor Gray
} else {
    Write-Host "Creating 3GB volume in Santiago..." -ForegroundColor Gray
    flyctl volumes create albedo_data --size 3 --region scl -a albedo-ai-team
    Write-Host "✅ Volume created" -ForegroundColor Green
}

Write-Host ""

# Step 4: Set secrets (CRITICAL - Never in Dockerfile!)
Write-Host "Step 4: Setting secrets securely..." -ForegroundColor Yellow
Write-Host "⚠️  IMPORTANT: Secrets are stored encrypted in Fly.io, NOT in the Docker image" -ForegroundColor Yellow
Write-Host ""

# Required secrets
$requiredSecrets = @(
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_USER_ID",
    "GITHUB_TOKEN"
)

# Optional secrets
$optionalSecrets = @(
    "TAVILY_API_KEY",
    "DAILY_BUDGET_ALERT",
    "MONTHLY_BUDGET_LIMIT"
)

Write-Host "Setting required secrets..." -ForegroundColor Gray
foreach ($secret in $requiredSecrets) {
    if ($envVars.ContainsKey($secret)) {
        $value = $envVars[$secret]
        $maskedValue = $value.Substring(0, [Math]::Min(10, $value.Length)) + "..."

        flyctl secrets set "$secret=$value" -a albedo-ai-team --stage 2>&1 | Out-Null
        Write-Host "  ✅ $secret = $maskedValue" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $secret - NOT FOUND in .env!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Setting optional secrets..." -ForegroundColor Gray
foreach ($secret in $optionalSecrets) {
    if ($envVars.ContainsKey($secret)) {
        $value = $envVars[$secret]
        flyctl secrets set "$secret=$value" -a albedo-ai-team --stage 2>&1 | Out-Null
        Write-Host "  ✅ $secret = $value" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $secret - Not found (optional)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "✅ All secrets set securely in Fly.io" -ForegroundColor Green
Write-Host ""

# Step 5: Deploy!
Write-Host "Step 5: Deploying to Fly.io..." -ForegroundColor Yellow
Write-Host "⏳ This may take 3-5 minutes..." -ForegroundColor Gray
Write-Host ""

flyctl deploy --ha=false -a albedo-ai-team

Write-Host ""
Write-Host "=== Deployment Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your app is now running at:" -ForegroundColor Cyan
Write-Host "  🌐 https://albedo-ai-team.fly.dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check status:" -ForegroundColor Yellow
Write-Host "  flyctl status -a albedo-ai-team" -ForegroundColor Gray
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  flyctl logs -a albedo-ai-team" -ForegroundColor Gray
Write-Host ""
Write-Host "SSH into the app:" -ForegroundColor Yellow
Write-Host "  flyctl ssh console -a albedo-ai-team" -ForegroundColor Gray
Write-Host ""
Write-Host "Test your Telegram bot now! 🤖" -ForegroundColor Green
Write-Host ""

Pause
