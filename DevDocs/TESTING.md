# DevDocs Testing System

This document provides instructions on how to use the comprehensive testing system for the DevDocs application.

## Overview

The testing system includes:

1. **Dev Test Center** - A web-based dashboard for running tests and viewing results
2. **Command-line Test Runner** - A script for running tests from the command line
3. **API Key Setup Guide** - Instructions for configuring API keys for various services

## Getting Started

### Prerequisites

- Node.js 14.x or higher
- npm or yarn
- A Supabase account
- A Google Cloud account (optional, for OCR and chatbot features)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aviadkim/backv2.git
   cd backv2/DevDocs
   ```

2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Create a `.env.local` file in the `frontend` directory with your API keys:
   ```
   # Supabase Configuration
   NEXT_PUBLIC_SUPABASE_URL=https://dnjnsotemnfrjlotgved.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

   # API Configuration
   NEXT_PUBLIC_API_URL=http://localhost:24125

   # Google Cloud Configuration (optional)
   NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/keyfile.json
   NEXT_PUBLIC_VISION_API_ENABLED=true
   NEXT_PUBLIC_CHATBOT_ENABLED=true
   ```

## Using the Dev Test Center

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:3002/dev-test-center
   ```

3. Use the interface to run tests, view results, and get recommendations for next steps.

## Running Tests from the Command Line

1. Run all tests:
   ```bash
   npm run dev:test
   ```

2. Run tests for a specific category:
   ```bash
   npm run dev:test -- frontend
   npm run dev:test -- backend
   npm run dev:test -- database
   npm run dev:test -- api
   npm run dev:test -- integration
   ```

## Configuring API Keys

1. Open your browser and navigate to:
   ```
   http://localhost:3002/api-key-setup
   ```

2. Follow the instructions to set up API keys for:
   - Supabase
   - Google Cloud
   - OCR Service
   - Chatbot Service

## Test Categories

The testing system includes tests for the following categories:

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

## Automated Fixes

The testing system can automatically fix some common issues:

1. In the Dev Test Center, enable the "Auto-fix issues when possible" option.
2. Run the tests.
3. The system will attempt to fix any issues it can.
4. Review the console output for details on the fixes applied.

## Next Steps

After running tests, the system will provide recommendations for next development steps based on the test results. These recommendations are prioritized to help you focus on the most critical issues first.

## Troubleshooting

If you encounter issues with the testing system:

1. Check your API key configuration in the `.env.local` file.
2. Make sure all dependencies are installed correctly.
3. Check the console output for error messages.
4. Try running the tests from the command line for more detailed error information.

## Contributing

When adding new features to the application, please also add corresponding tests to ensure code quality and prevent regressions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
