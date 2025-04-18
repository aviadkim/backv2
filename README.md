# FinDoc - Financial Document Analyzer

FinDoc is a powerful financial document analysis platform that helps users extract, analyze, and visualize financial data from various document types. Built with a modern serverless architecture using Next.js, Vercel, and Supabase.

## Features

- **Document Upload and Storage**: Securely upload and store financial documents in various formats (PDF, Excel, CSV, images)
- **OCR and Document Processing**: Extract text and tables from documents using advanced OCR techniques optimized for Hebrew
- **RAG Multimodal Financial Document Processor**: Process financial documents using Retrieval-Augmented Generation (RAG) and multimodal AI models
- **Financial Data Analysis**: Analyze financial data, identify securities, calculate portfolio metrics
- **Query Engine**: Ask natural language questions about your financial documents
- **Document Comparison**: Compare multiple financial documents to identify changes and trends
- **Data Export**: Export financial data in various formats (Excel, CSV, PDF, JSON)
- **Financial Advisor**: Get personalized recommendations and insights based on portfolio analysis
- **Multi-tenant Architecture**: Secure isolation of client data
- **AI Agents**: Intelligent agents for document analysis and insights
- **Data Visualization**: Interactive charts and dashboards
- **Security & Compliance**: GDPR compliance, data encryption, and audit logging
- **Performance Optimization**: Caching and monitoring for optimal performance

## Tech Stack

- **Frontend**: Next.js, React, Chakra UI
- **Backend**: Express.js, Node.js
- **API**: Next.js API Routes and Express.js
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Deployment**: Google Cloud Run
- **AI**: OpenRouter API (Claude, GPT-4), RAG (Retrieval-Augmented Generation)
- **OCR**: Tesseract, Camelot, PDFPlumber
- **Authentication**: JWT, bcrypt
- **Security**: Helmet, crypto
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Data Visualization**: Chart.js
- **Export**: ExcelJS, PDFKit, json2csv

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Supabase account
- Vercel account (for deployment)

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/aviadkim/backv2.git
   cd backv2
   ```

2. Copy `.env.example` to `.env.local` and fill in your Supabase credentials:
   ```
   cp .env.example .env.local
   ```

3. Install dependencies:
   ```
   cd DevDocs
   npm install
   ```

4. Run the development server:
   ```
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment

This project is configured for deployment on both Vercel and Google Cloud Run:

### Vercel Deployment

The frontend can be deployed on Vercel with Supabase as the database and storage solution.

See [VERCEL_SUPABASE_DEPLOYMENT.md](VERCEL_SUPABASE_DEPLOYMENT.md) for detailed Vercel deployment instructions.

### Google Cloud Run Deployment

The backend can be deployed as a containerized application on Google Cloud Run using Docker and GitHub Actions.

See [DevDocs/DEPLOYMENT.md](DevDocs/DEPLOYMENT.md) for detailed Google Cloud Run deployment instructions.

## Development Roadmap

See [DevDocs/ROADMAP.md](DevDocs/ROADMAP.md) for the detailed development plan. The roadmap outlines a 12-week development process that has been completed, covering everything from initial setup to performance optimization and deployment.

## API Documentation

### Authentication

- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Login and get JWT token
- `POST /api/auth/refresh`: Refresh JWT token
- `GET /api/auth/me`: Get current user information

### Documents

- `POST /api/documents`: Upload a document
- `GET /api/documents`: Get all documents
- `GET /api/documents/:id`: Get a document by ID
- `PUT /api/documents/:id`: Update a document
- `DELETE /api/documents/:id`: Delete a document
- `GET /api/documents/:id/download`: Download a document

### OCR

- `POST /api/ocr/process/:id`: Process a document with OCR
- `POST /api/ocr/detect-tables/:id`: Detect tables in a document
- `POST /api/ocr/process-image`: Process an image with OCR
- `GET /api/ocr/results/:id`: Get OCR results for a document
- `GET /api/ocr/table-results/:id`: Get table detection results for a document

### Financial Analysis

- `POST /api/financial/analyze/:id`: Analyze financial data in a document
- `GET /api/financial/data/:id`: Get financial data for a document
- `GET /api/financial/portfolio/:id`: Get portfolio summary for a document
- `GET /api/financial/securities/:id`: Get securities for a document
- `GET /api/financial/asset-allocation/:id`: Get asset allocation for a document

### RAG Multimodal Processing

- `POST /api/enhanced/process`: Process a document with RAG Multimodal Processor
- `GET /api/enhanced/status/:taskId`: Get processing status
- `GET /api/enhanced/result/:taskId`: Get processing result
- `GET /api/enhanced/visualizations/:taskId`: Get visualizations

### Query Engine

- `POST /api/query/answer/:id`: Answer a query about a document
- `GET /api/query/history/:id`: Get previous queries for a document

### Document Comparison

- `POST /api/comparison/compare`: Compare two documents
- `GET /api/comparison/:id`: Get comparison result
- `GET /api/comparison/history/:id`: Get comparison history for a document

### Data Export

- `POST /api/export/:id`: Export document data
- `GET /api/export/formats`: Get export formats

### Financial Advisor

- `POST /api/advisor/analyze/:id`: Analyze portfolio and provide recommendations
- `GET /api/advisor/analysis/:id`: Get advisor analysis for a document
- `GET /api/advisor/recommendations/:id`: Get recommendations for a document
- `GET /api/advisor/risk/:id`: Get risk analysis for a document

## Database Schema

The database schema is defined in [supabase/schema.sql](supabase/schema.sql) and includes tables for:

- Users (profiles)
- Organizations
- Documents
- Financial data
- ISINs
- API keys

## Security

### API Keys and Secrets

This project uses several API keys and secrets that should never be committed to the repository:

- **OpenRouter API Key**: Used for AI-enhanced document processing
- **Google Cloud Service Account Credentials**: Used for deployment to Google Cloud Run
- **Database Credentials**: Used for connecting to the database

### Best Practices

1. **Environment Variables**: Store all secrets as environment variables. Copy `.env.template` to `.env` and fill in your values.

2. **Secret Management**: Use Google Secret Manager or GitHub Secrets for CI/CD pipelines.

3. **Access Control**: Limit access to production environments and secrets to only those who need it.

4. **Audit**: Regularly audit access to secrets and rotate them periodically.

5. **Git Hygiene**: Never commit secrets to the repository. Use `.gitignore` to prevent accidental commits.

### Security Reporting

If you discover a security vulnerability, please send an email to aviadkim@gmail.com. All security vulnerabilities will be promptly addressed.

## License

This project is proprietary and confidential.

## Contact

For questions or support, please contact aviadkim@gmail.com.
