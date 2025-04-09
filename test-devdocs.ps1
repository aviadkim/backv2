# DevDocs Test Script
# This script tests the DevDocs application components

Write-Host "Running Comprehensive DevDocs Test Suite..." -ForegroundColor Green

# Navigate to the DevDocs directory
Set-Location -Path "c:\Users\aviad\OneDrive\Desktop\backv2\DevDocs"
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan

# Create test results directory if it doesn't exist
if (-not (Test-Path -Path ".\test-results")) {
    New-Item -ItemType Directory -Path ".\test-results" | Out-Null
    Write-Host "Created test results directory" -ForegroundColor Yellow
}

# Configuration
$backendUrl = "http://localhost:24125"
$frontendUrl = "http://localhost:3002"
$logFile = ".\test-results\test-log-$(Get-Date -Format 'yyyy-MM-dd-HHmmss').txt"

# Start logging
Start-Transcript -Path $logFile

# Function to check if a service is running
function Test-ServiceRunning {
    param (
        [string]$Url,
        [string]$Name
    )
    
    try {
        Write-Host "Testing connection to $Name at $Url..." -ForegroundColor Cyan
        $response = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -TimeoutSec 5
        
        if ($response.StatusCode -eq 200) {
            Write-Host "$Name is running (Status 200 OK)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "$Name returned status code $($response.StatusCode)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "$Name is not responding: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to reset database for testing
function Reset-Database {
    try {
        Write-Host "Resetting database to initial state..." -ForegroundColor Cyan
        $response = Invoke-WebRequest -Uri "$backendUrl/api/reset" -Method POST -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            Write-Host "Database reset successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to reset database: $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "Error resetting database: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test document API
function Test-DocumentApi {
    try {
        Write-Host "Testing document API..." -ForegroundColor Cyan
        
        # Get all documents
        $response = Invoke-WebRequest -Uri "$backendUrl/api/documents" -Method GET -UseBasicParsing
        $documents = ($response.Content | ConvertFrom-Json).documents
        
        Write-Host "Found $($documents.Count) documents" -ForegroundColor Green
        
        # Get first document
        if ($documents.Count -gt 0) {
            $docId = $documents[0].id
            $response = Invoke-WebRequest -Uri "$backendUrl/api/documents/$docId" -Method GET -UseBasicParsing
            $document = $response.Content | ConvertFrom-Json
            
            Write-Host "Retrieved document: $($document.title)" -ForegroundColor Green
        }
        
        # Test search
        $response = Invoke-WebRequest -Uri "$backendUrl/api/documents?q=python" -Method GET -UseBasicParsing
        $searchResults = ($response.Content | ConvertFrom-Json).documents
        
        Write-Host "Search for 'python' returned $($searchResults.Count) results" -ForegroundColor Green
        
        # Test tag filter
        $response = Invoke-WebRequest -Uri "$backendUrl/api/documents?tag=web" -Method GET -UseBasicParsing
        $tagResults = ($response.Content | ConvertFrom-Json).documents
        
        Write-Host "Tag filter for 'web' returned $($tagResults.Count) results" -ForegroundColor Green
        
        # Get all tags
        $response = Invoke-WebRequest -Uri "$backendUrl/api/tags" -Method GET -UseBasicParsing
        $tags = ($response.Content | ConvertFrom-Json).tags
        
        Write-Host "Found $($tags.Count) unique tags" -ForegroundColor Green
        
        return $true
    } catch {
        Write-Host "Error testing document API: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to create a test document
function New-TestDocument {
    try {
        Write-Host "Creating test document..." -ForegroundColor Cyan
        
        $document = @{
            title = "PowerShell Test Document"
            content = "This is a test document created by the PowerShell test script at $(Get-Date)"
            tags = @("test", "powershell", "automation")
        }
        
        $body = $document | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "$backendUrl/api/documents" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
        
        $newDocument = $response.Content | ConvertFrom-Json
        
        Write-Host "Created document with ID: $($newDocument.id)" -ForegroundColor Green
        
        return $newDocument.id
    } catch {
        Write-Host "Error creating test document: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function to update a test document
function Update-TestDocument {
    param (
        [string]$DocumentId
    )
    
    try {
        Write-Host "Updating document $DocumentId..." -ForegroundColor Cyan
        
        $document = @{
            title = "Updated PowerShell Test Document"
            content = "This document was updated by the PowerShell test script at $(Get-Date)"
            tags = @("test", "powershell", "updated")
        }
        
        $body = $document | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "$backendUrl/api/documents/$DocumentId" -Method PUT -Body $body -ContentType "application/json" -UseBasicParsing
        
        $updatedDocument = $response.Content | ConvertFrom-Json
        
        Write-Host "Updated document: $($updatedDocument.title)" -ForegroundColor Green
        
        return $true
    } catch {
        Write-Host "Error updating document: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to delete a test document
function Remove-TestDocument {
    param (
        [string]$DocumentId
    )
    
    try {
        Write-Host "Deleting document $DocumentId..." -ForegroundColor Cyan
        
        $response = Invoke-WebRequest -Uri "$backendUrl/api/documents/$DocumentId" -Method DELETE -UseBasicParsing
        
        $result = $response.Content | ConvertFrom-Json
        
        Write-Host $result.message -ForegroundColor Green
        
        return $true
    } catch {
        Write-Host "Error deleting document: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to run Playwright tests
function Start-PlaywrightTests {
    try {
        Write-Host "Running Playwright tests..." -ForegroundColor Cyan
        
        # Navigate to project root
        Set-Location -Path "c:\Users\aviad\OneDrive\Desktop\backv2\DevDocs"
        
        # Run a single test first to check if it works
        npx playwright test -g "homepage loads" --headed
        
        Write-Host "Playwright test completed" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Error running Playwright tests: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test document detail page
function Test-DocumentDetailPage {
    param (
        [string]$DocumentId = "1"
    )
    
    try {
        Write-Host "Testing document detail page for document $DocumentId..." -ForegroundColor Cyan
        
        $url = "$frontendUrl/document/$DocumentId"
        Write-Host "Opening $url in default browser..." -ForegroundColor Cyan
        Start-Process $url
        
        Write-Host "Document detail page test initiated" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Error testing document detail page: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test document edit page
function Test-DocumentEditPage {
    param (
        [string]$DocumentId = "1"
    )
    
    try {
        Write-Host "Testing document edit page for document $DocumentId..." -ForegroundColor Cyan
        
        $url = "$frontendUrl/edit/$DocumentId"
        Write-Host "Opening $url in default browser..." -ForegroundColor Cyan
        Start-Process $url
        
        Write-Host "Document edit page test initiated" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Error testing document edit page: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main test execution
Write-Host "Starting DevDocs API Tests" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Step 1: Check if services are running
$backendRunning = Test-ServiceRunning -Url "$backendUrl/api/health" -Name "Backend API"

if ($backendRunning) {
    # Step 2: Reset database
    Reset-Database
    
    # Step 3: Test document API
    Test-DocumentApi
    
    # Step 4: Create test document
    $docId = New-TestDocument
    
    if ($docId) {
        # Step 5: Update test document
        Update-TestDocument -DocumentId $docId
        
        # Step 6: Test document detail page
        Test-DocumentDetailPage -DocumentId $docId
        
        # Step 7: Test document edit page
        Test-DocumentEditPage -DocumentId $docId
        
        # Step 8: Delete test document
        Remove-TestDocument -DocumentId $docId
    }
    
    # Step 9: Run Playwright tests for specific components
    Write-Host "Running specific Playwright test for document pages..." -ForegroundColor Cyan
    try {
        npx playwright test -g "document detail" --headed
    } catch {
        Write-Host "Playwright test error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Please make sure the DevDocs backend is running at $backendUrl" -ForegroundColor Red
}

Write-Host "Tests completed" -ForegroundColor Cyan
Stop-Transcript
