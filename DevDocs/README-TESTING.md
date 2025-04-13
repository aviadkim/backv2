# DevDocs Testing System

This document provides a quick guide on how to use the comprehensive testing system for the DevDocs application.

## Quick Start

### Web-based Testing Dashboard

1. Start the development server:
   ```
   cd DevDocs/frontend
   npm run dev
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:3002/dev-test-center
   ```

3. Use the interface to run tests, view results, and get recommendations for next steps.

### Command-line Testing

Run tests from the command line using the provided batch file:

```
cd DevDocs
run-tests.bat
```

To run tests for a specific category:
```
run-tests.bat frontend
run-tests.bat backend
run-tests.bat database
run-tests.bat api
run-tests.bat integration
```

## Features

The testing system includes:

1. **Dev Test Center** - A web-based dashboard for running tests and viewing results
2. **Command-line Test Runner** - A script for running tests from the command line
3. **API Key Setup Guide** - Instructions for configuring API keys for various services
4. **Automated Fixes** - Automatic fixing of common issues
5. **Development Recommendations** - Suggestions for next development steps

## API Key Setup

Configure your API keys by visiting:
```
http://localhost:3002/api-key-setup
```

This page provides detailed instructions for setting up:
- Supabase API keys
- Google Cloud API keys
- OCR service configuration
- Chatbot service configuration

## Test Categories

The testing system covers the following categories:

### Frontend
- UI Components
- Routing
- State Management
- Form Validation
- Responsive Design

### Backend
- API Endpoints
- Authentication
- File Processing
- Error Handling
- Logging

### Database
- Supabase Connection
- Query Performance
- Data Integrity
- Migrations
- Backup & Restore

### API
- Google Cloud Connection
- OCR API
- Chatbot API
- Rate Limiting
- Response Format

### Integration
- Frontend-Backend
- Backend-Database
- API Integration
- Authentication Flow
- End-to-End

## Troubleshooting

If you encounter issues with the testing system:

1. Check your API key configuration in the `.env.local` file
2. Make sure all dependencies are installed correctly
3. Check the console output for error messages
4. Try running the tests from the command line for more detailed error information

For more detailed information, see the [TESTING.md](TESTING.md) file.
