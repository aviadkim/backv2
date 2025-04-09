# MCP Installation Script for FinDoc
# This script installs all the necessary tools for the MCP architecture

Write-Host "Installing MCP tools for FinDoc..." -ForegroundColor Green

# Navigate to the frontend directory
Set-Location -Path "DevDocs/frontend"

# Install TypeScript
Write-Host "Installing TypeScript..." -ForegroundColor Cyan
npm install --save-dev typescript @types/react @types/node

# Install ESLint and Prettier
Write-Host "Installing ESLint and Prettier..." -ForegroundColor Cyan
npm install --save-dev eslint prettier eslint-config-prettier eslint-plugin-react

# Install Husky and lint-staged for pre-commit hooks
Write-Host "Installing Husky and lint-staged..." -ForegroundColor Cyan
npm install --save-dev husky lint-staged

# Install Jest and React Testing Library
Write-Host "Installing Jest and React Testing Library..." -ForegroundColor Cyan
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Install Supabase client
Write-Host "Installing Supabase client..." -ForegroundColor Cyan
npm install @supabase/supabase-js

# Create directories if they don't exist
Write-Host "Creating MCP directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "models"
New-Item -ItemType Directory -Force -Path "controllers"
New-Item -ItemType Directory -Force -Path "providers"
New-Item -ItemType Directory -Force -Path "repositories"
New-Item -ItemType Directory -Force -Path "templates"
New-Item -ItemType Directory -Force -Path "scripts"

# Return to the root directory
Set-Location -Path "../.."

Write-Host "MCP installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To generate new MCP components, use the following commands:" -ForegroundColor Yellow
Write-Host "  cd DevDocs/frontend" -ForegroundColor Yellow
Write-Host "  npm run mcp:model -- ModelName 'Description'" -ForegroundColor Yellow
Write-Host "  npm run mcp:controller -- ControllerName 'Description'" -ForegroundColor Yellow
Write-Host "  npm run mcp:provider -- ProviderName 'Description'" -ForegroundColor Yellow
Write-Host "  npm run mcp:repository -- RepositoryName 'Description'" -ForegroundColor Yellow
Write-Host "  npm run mcp:all -- ComponentName 'Description'" -ForegroundColor Yellow
Write-Host ""
Write-Host "Example:" -ForegroundColor Yellow
Write-Host "  npm run mcp:all -- Document 'Document management'" -ForegroundColor Yellow
