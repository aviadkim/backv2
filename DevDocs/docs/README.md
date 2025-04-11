# Financial Document Analysis Application

This application provides comprehensive tools for analyzing financial documents, managing portfolios, and generating financial reports.

## Overview

The Financial Document Analysis Application is designed to help financial professionals with:

- Analyzing financial documents (annual reports, financial statements, portfolio statements)
- Managing and analyzing investment portfolios
- Generating comprehensive financial reports
- Providing AI-powered financial insights and recommendations

## Components

The application consists of several key components:

1. **Financial Document Processor**: Extracts financial data from various document types
2. **Portfolio Analyzer**: Analyzes investment portfolios and calculates key metrics
3. **Report Generator**: Generates financial reports in various formats
4. **AI Analysis**: Provides AI-powered financial insights and recommendations
5. **Frontend UI**: User interface for interacting with the application

## Architecture

The application follows a client-server architecture:

- **Backend**: Python-based API server with financial processing capabilities
- **Frontend**: React-based user interface
- **Database**: SQL database for storing financial data
- **Storage**: File storage for documents and reports
- **AI Services**: Integration with AI services for advanced analysis

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL or Supabase account
- OpenAI API key (for AI features)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/aviadkim/backv2.git
   cd backv2
   ```

2. Install backend dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```
   cd ../frontend
   npm install
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```
   # Start the backend
   cd backend
   python app.py
   
   # Start the frontend (in a new terminal)
   cd frontend
   npm run dev
   ```

## Usage

See the [User Guide](user_guide.md) for detailed usage instructions.

## API Reference

See the [API Documentation](api_docs.md) for details on the available API endpoints.

## Contributing

See the [Contributing Guide](contributing.md) for details on how to contribute to the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
