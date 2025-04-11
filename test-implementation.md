# Testing the FinDoc Implementation

This document provides instructions for testing the implemented features of the FinDoc application.

## Prerequisites

1. Make sure you have the following installed:
   - Node.js 18+
   - Python 3.8+
   - Git

2. Clone the repository:
   ```bash
   git clone https://github.com/aviadkim/backv2.git
   cd backv2
   ```

3. Install dependencies:
   ```bash
   cd DevDocs/frontend
   npm install
   cd ../backend
   pip install -r requirements.txt
   ```

4. Start the development server:
   ```bash
   cd ../..
   ./run-findoc-enhanced.ps1
   ```

## Test Cases

### 1. Authentication System

#### 1.1 User Registration

1. Navigate to http://localhost:3002/signup
2. Fill in the registration form with:
   - Full Name: Test User
   - Email: test@example.com
   - Password: Password123!
   - Confirm Password: Password123!
3. Click "Create Account"
4. Verify that you receive a success message
5. Verify that you are redirected to the login page

#### 1.2 User Login

1. Navigate to http://localhost:3002/login
2. Enter the credentials:
   - Email: test@example.com
   - Password: Password123!
3. Click "Sign in"
4. Verify that you are redirected to the dashboard

#### 1.3 Password Reset

1. Navigate to http://localhost:3002/forgot-password
2. Enter the email: test@example.com
3. Click "Send Reset Instructions"
4. Verify that you receive a success message

### 2. Document Upload and Processing

#### 2.1 Document Upload

1. Navigate to http://localhost:3002/test-upload
2. Click "Browse Files" or drag and drop a PDF file
3. Add a title and some tags
4. Click "Upload Files"
5. Verify that the document appears in the "Uploaded Documents" section
6. Verify that the document processing information is displayed

#### 2.2 Document Processing

1. Upload a financial document (PDF, Excel, or CSV)
2. Verify that the document is processed correctly
3. Check that financial data is extracted (ISINs, tables, etc.)
4. Verify that the document appears in the dashboard's recent documents

### 3. Financial Data Visualization

#### 3.1 Portfolio Visualization

1. Navigate to http://localhost:3002/test-visualization
2. Select "Portfolio Allocation"
3. Verify that the doughnut chart displays correctly
4. Try different chart types (pie, bar, line)
5. Verify that the summary information is displayed

#### 3.2 Time Series Visualization

1. Navigate to http://localhost:3002/test-visualization
2. Select "Time Series"
3. Verify that the line chart displays correctly
4. Check that the summary information shows start value, end value, and change

#### 3.3 Comparison Visualization

1. Navigate to http://localhost:3002/test-visualization
2. Select "Comparison"
3. Verify that the bar chart displays correctly
4. Check that multiple series are displayed

### 4. Dashboard

1. Navigate to http://localhost:3002/dashboard
2. Verify that the welcome message displays correctly
3. Check that recent documents are displayed
4. Verify that the portfolio overview is displayed
5. Test the "Upload Document" button
6. Test navigation to other pages

## Expected Results

- All authentication flows should work smoothly
- Document upload should be intuitive and provide feedback
- Document processing should extract relevant financial information
- Financial visualizations should be clear and interactive
- Dashboard should provide a comprehensive overview

## Troubleshooting

### Authentication Issues

- Check that Supabase is properly configured
- Verify that environment variables are set correctly
- Check browser console for errors

### Document Upload Issues

- Ensure the upload directory exists and is writable
- Check file size limits
- Verify that the API endpoint is accessible

### Visualization Issues

- Check that Chart.js is properly installed
- Verify that data is in the correct format
- Check browser console for errors

## Reporting Issues

If you encounter any issues during testing, please:

1. Take a screenshot of the error
2. Note the steps to reproduce
3. Check the browser console for errors
4. Check the server logs for errors
5. Create an issue in the GitHub repository with all the information
