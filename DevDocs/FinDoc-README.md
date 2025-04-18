# FinDoc Analyzer - Financial Document Processing System

FinDoc Analyzer is a comprehensive financial document processing system designed to extract, analyze, and visualize financial data from various document types. The system uses advanced OCR, AI-enhanced data extraction, and financial analysis algorithms to provide accurate insights from financial documents.

## Features

- **Document Upload**: Upload and process PDF, Excel, and CSV files
- **Financial Data Extraction**: Automatically extract ISINs, financial metrics, and key data
- **Portfolio Analysis**: Analyze investment portfolios with advanced metrics
- **AI Agents**: Intelligent agents for document analysis and insights
- **Data Visualization**: Interactive charts and dashboards
- **Multi-tenant Architecture**: Secure isolation of client data
- **Advanced OCR**: Hebrew language support with enhanced accuracy
- **Document Integration**: Combine data from multiple financial documents
- **Security & Compliance**: GDPR compliance, data encryption, and audit logging
- **Performance Optimization**: Caching and monitoring for optimal performance

## Project Structure

```
DevDocs/
├── backend/              # Express.js backend
│   ├── agents/           # AI agents for document processing
│   ├── controllers/      # Business logic controllers
│   ├── db/               # Database schemas and migrations
│   ├── middleware/       # Express middleware
│   ├── models/           # Data models
│   ├── routes/           # API routes
│   ├── services/         # Business services
│   ├── tests/            # Test files
│   └── utils/            # Utility functions
│
├── frontend/             # Next.js frontend
│   ├── components/       # React components
│   ├── contexts/         # React contexts
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utility functions
│   ├── pages/            # Next.js pages
│   ├── providers/        # Context providers
│   ├── public/           # Static assets
│   └── styles/           # CSS and styling
│
└── docs/                 # Documentation
    ├── api/              # API documentation
    ├── deployment/       # Deployment guides
    ├── development/      # Development guides
    └── user-guides/      # User guides
```

## Technology Stack

- **Frontend**: Next.js, React, TailwindCSS
- **Backend**: Express.js, Node.js
- **API**: Next.js API Routes and Express.js
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Deployment**: Vercel, Google Cloud Run
- **AI**: OpenRouter API, Google ADK
- **Authentication**: Supabase Auth, JWT
- **Security**: bcrypt, crypto, helmet
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## Getting Started

### Prerequisites

- Node.js 18 or higher
- Docker (for containerization)
- Supabase account
- OpenRouter API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/aviadkim/backv2.git
   cd backv2
   ```

2. Install backend dependencies:
   ```
   cd DevDocs/backend
   npm install
   ```

3. Install frontend dependencies:
   ```
   cd ../frontend
   npm install
   ```

4. Create a `.env` file in the `DevDocs/backend` directory with the following environment variables:
   ```
   NODE_ENV=development
   PORT=3001
   OPENROUTER_API_KEY=your_openrouter_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   JWT_SECRET=your_jwt_secret
   ENCRYPTION_KEY=your_encryption_key
   ```

5. Create a `.env.local` file in the `DevDocs/frontend` directory with the following environment variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   NEXT_PUBLIC_API_URL=http://localhost:3001
   ```

6. Start the backend server:
   ```
   cd ../backend
   npm run dev
   ```

7. Start the frontend development server:
   ```
   cd ../frontend
   npm run dev
   ```

8. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Docker Development

1. Build and run the Docker containers:
   ```
   docker-compose up
   ```

2. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment

### Google Cloud Run Deployment

1. Build the Docker image:
   ```
   docker build -t gcr.io/github-456508/findoc-analyzer:latest -f Dockerfile.optimized .
   ```

2. Push the image to Google Container Registry:
   ```
   docker push gcr.io/github-456508/findoc-analyzer:latest
   ```

3. Deploy to Google Cloud Run:
   ```
   gcloud run deploy findoc-analyzer \
     --image gcr.io/github-456508/findoc-analyzer:latest \
     --platform managed \
     --region me-west1 \
     --allow-unauthenticated \
     --set-env-vars="NODE_ENV=production,OPENROUTER_API_KEY=your_key"
   ```

## Available Agents

The FinDoc Analyzer includes several agents for financial document processing:

1. **DocumentPreprocessorAgent**: Optimizes document images for better OCR results
2. **HebrewOCRAgent**: Extracts text from documents with Hebrew content
3. **ISINExtractorAgent**: Identifies and validates ISIN codes in financial documents
4. **FinancialTableDetectorAgent**: Identifies and extracts tables from financial documents
5. **FinancialDataAnalyzerAgent**: Analyzes and organizes financial information from documents
6. **DocumentIntegrationAgent**: Integrates all extracted data into a unified structure
7. **QueryEngineAgent**: Answers natural language questions about financial documents
8. **NotificationAgent**: Creates user notifications based on document data
9. **DataExportAgent**: Exports data to various formats for use in other systems
10. **DocumentComparisonAgent**: Compares documents and identifies changes and developments
11. **FinancialAdvisorAgent**: Provides financial analysis, accounting, and investment advice

## API Endpoints

The FinDoc Analyzer provides several API endpoints:

- `GET /api/health`: Health check endpoint
- `GET /api/health/db`: Database health check endpoint
- `GET /api/health/dependencies`: Dependencies health check endpoint

### Financial Agents API Endpoints

- `POST /api/financial/process-document`: Process a financial document
- `POST /api/financial/export-data`: Export data to various formats
- `POST /api/financial/compare-documents`: Compare documents and identify changes
- `POST /api/financial/query-document`: Query document data using natural language
- `POST /api/financial/integrate-documents`: Integrate multiple documents
- `POST /api/financial/ocr-document`: Extract text from documents using OCR
- `GET /api/integration/external-systems`: Get information about external system integrations

## License

© 2023 FinDoc. All rights reserved.
