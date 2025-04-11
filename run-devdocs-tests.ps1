# DevDocs Testing Script
# This script runs comprehensive tests for the DevDocs application

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DevDocs Testing Suite" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Step 1: Test the backend API
Write-Host "`nStep 1: Testing Backend API..." -ForegroundColor Yellow
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

# Define test endpoints
$baseUrl = "http://localhost:24125"
$endpoints = @(
    @{Path = ""; Description = "Root endpoint"},
    @{Path = "/api/health"; Description = "Health endpoint"},
    @{Path = "/api/documents"; Description = "Documents endpoint"},
    @{Path = "/api/tags"; Description = "Tags endpoint"},
    @{Path = "/api/documents/1"; Description = "Specific document endpoint"}
)

# Track API test success
$apiSuccess = $true

# Test each endpoint
foreach ($endpoint in $endpoints) {
    $url = "$baseUrl$($endpoint.Path)"
    Write-Host "Testing $($endpoint.Description) at $url..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -UseBasicParsing -TimeoutSec 5
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ SUCCESS - Status Code: $($response.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "✗ FAILED - Status Code: $($response.StatusCode)" -ForegroundColor Red
            $apiSuccess = $false
        }
    } catch {
        Write-Host "✗ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
        $apiSuccess = $false
    }
}

# Step 2: Test document creation
Write-Host "`nStep 2: Testing Document Creation..." -ForegroundColor Yellow
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

$newDocument = @{
    title = "Test Document"
    content = "This is a test document created by the testing script."
    tags = @("test", "automation")
} | ConvertTo-Json

$documentCreated = $false
$documentId = $null

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/documents" -Method POST -Body $newDocument -ContentType "application/json"
    $documentId = $response.id
    Write-Host "✓ SUCCESS - Document created with ID: $documentId" -ForegroundColor Green
    $documentCreated = $true
} catch {
    Write-Host "✗ FAILED - Error creating document: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 3: Test document retrieval (if creation succeeded)
if ($documentCreated) {
    Write-Host "`nStep 3: Testing Document Retrieval..." -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/documents/$documentId" -Method GET
        if ($response.title -eq "Test Document") {
            Write-Host "✓ SUCCESS - Document retrieved successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ FAILED - Document content doesn't match" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ FAILED - Error retrieving document: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Step 4: Test document update
    Write-Host "`nStep 4: Testing Document Update..." -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    $updatedDocument = @{
        id = $documentId
        title = "Updated Test Document"
        content = "This document was updated by the testing script."
        tags = @("test", "automation", "updated")
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/documents/$documentId" -Method PUT -Body $updatedDocument -ContentType "application/json"
        if ($response.title -eq "Updated Test Document") {
            Write-Host "✓ SUCCESS - Document updated successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ FAILED - Document update failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ FAILED - Error updating document: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Step 5: Test document deletion
    Write-Host "`nStep 5: Testing Document Deletion..." -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/documents/$documentId" -Method DELETE
        Write-Host "✓ SUCCESS - Document deleted successfully" -ForegroundColor Green
        
        # Verify deletion
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/api/documents/$documentId" -Method GET
            Write-Host "✗ FAILED - Document still exists after deletion" -ForegroundColor Red
        } catch {
            if ($_.Exception.Response.StatusCode.value__ -eq 404) {
                Write-Host "✓ SUCCESS - Document confirmed deleted (404 Not Found)" -ForegroundColor Green
            } else {
                Write-Host "? INCONCLUSIVE - Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "✗ FAILED - Error deleting document: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Step 6: Test frontend URL
Write-Host "`nStep 6: Checking Frontend Accessibility..." -ForegroundColor Yellow
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3002" -Method GET -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ SUCCESS - Frontend is accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ FAILED - Frontend returned status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ FAILED - Frontend is not accessible: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure the frontend server is running at http://localhost:3002" -ForegroundColor Yellow
}

# Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "Backend API: $(if ($apiSuccess) { "PASSED ✓" } else { "FAILED ✗" })" -ForegroundColor $(if ($apiSuccess) { "Green" } else { "Red" })
Write-Host "Document CRUD: $(if ($documentCreated) { "TESTED ✓" } else { "NOT TESTED ✗" })" -ForegroundColor $(if ($documentCreated) { "Green" } else { "Yellow" })

Write-Host "`nTo run the application:" -ForegroundColor Cyan
Write-Host "1. Start the backend: cd DevDocs\backend; python app.py" -ForegroundColor White
Write-Host "2. Start the frontend: cd DevDocs\frontend; npm run dev" -ForegroundColor White
Write-Host "3. Access the app at: http://localhost:3002" -ForegroundColor White

Write-Host "`nNext steps in development:" -ForegroundColor Cyan
Write-Host "- Implement user authentication (Step 18)" -ForegroundColor White
Write-Host "- Add agent integration for document processing (Step 19)" -ForegroundColor White
Write-Host "- Enhance user experience with feedback and transitions (Step 20)" -ForegroundColor White
