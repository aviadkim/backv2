# PowerShell script to set up local development environment

# Create .env file for local development
Write-Host "Setting up local development environment..." -ForegroundColor Cyan

# Check if .env file already exists
if (Test-Path ".env") {
    $overwrite = Read-Host -Prompt ".env file already exists. Overwrite? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Ask for API keys
$openRouterApiKey = Read-Host -Prompt "Enter your OpenRouter API Key"
$supabaseUrl = Read-Host -Prompt "Enter your Supabase URL (e.g., https://your-project-id.supabase.co)"
$supabaseKey = Read-Host -Prompt "Enter your Supabase Key"

# Create .env file
$envContent = @"
# Local development environment variables
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

# Supabase configuration
SUPABASE_URL=$supabaseUrl
SUPABASE_KEY=$supabaseKey

# OpenRouter API key
OPENROUTER_API_KEY=$openRouterApiKey

# Node environment
NODE_ENV=development
"@

# Write to .env file
$envContent | Out-File -FilePath ".env" -Encoding utf8

Write-Host "Local environment setup complete!" -ForegroundColor Green
Write-Host "The .env file has been created with your API keys." -ForegroundColor Cyan
Write-Host "IMPORTANT: Do not commit the .env file to version control." -ForegroundColor Yellow

# Add .env to .gitignore if it's not already there
$gitignoreContent = Get-Content ".gitignore" -ErrorAction SilentlyContinue
if ($gitignoreContent -notcontains ".env") {
    Write-Host "Adding .env to .gitignore..." -ForegroundColor Cyan
    Add-Content -Path ".gitignore" -Value "`n# Local environment variables`n.env"
}

# Install dependencies
$installDeps = Read-Host -Prompt "Install dependencies? (y/n)"
if ($installDeps -eq "y") {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
}

Write-Host "Setup complete! You can now run 'npm run dev' to start the development server." -ForegroundColor Green
