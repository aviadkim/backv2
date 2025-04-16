# Safe push script that avoids pushing sensitive files

# Make sure .gitignore is properly set up
Write-Host "Checking .gitignore configuration..."
$gitignore = Get-Content .gitignore
$requiredEntries = @(
    "key.json",
    "**/github-service-account-key.json",
    "**/service-account-key.json"
)

$missingEntries = $false
foreach ($entry in $requiredEntries) {
    if ($gitignore -notcontains $entry) {
        Write-Host "Warning: $entry is not in .gitignore" -ForegroundColor Yellow
        $missingEntries = $true
    }
}

if ($missingEntries) {
    Write-Host "Please update .gitignore before continuing" -ForegroundColor Red
    exit 1
}

# Check for sensitive files that might be staged
Write-Host "Checking for sensitive files in staging area..."
$stagedFiles = git diff --name-only --cached
$sensitivePatterns = @(
    "key.json",
    "github-service-account-key.json",
    "service-account-key.json"
)

$hasSensitiveFiles = $false
foreach ($file in $stagedFiles) {
    foreach ($pattern in $sensitivePatterns) {
        if ($file -like "*$pattern*") {
            Write-Host "Warning: Sensitive file detected in staging area: $file" -ForegroundColor Red
            $hasSensitiveFiles = $true
        }
    }
}

if ($hasSensitiveFiles) {
    Write-Host "Please unstage sensitive files before continuing" -ForegroundColor Red
    exit 1
}

# Add all files except sensitive ones
Write-Host "Adding files to git..."
git add .

# Commit changes
Write-Host "Committing changes..."
git commit -m "Add FinDoc Analyzer v1.0 - Comprehensive financial document processing solution"

# Push to GitHub
Write-Host "Pushing to GitHub..."
git push origin main

Write-Host "Code pushed to GitHub. The GitHub Actions workflow will deploy the application to Google Cloud Run."
Write-Host "You can monitor the deployment in the Actions tab of your GitHub repository."
