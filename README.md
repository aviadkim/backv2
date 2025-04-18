# FinDoc - Financial Document Analyzer

FinDoc is a powerful financial document analysis platform that helps users extract, analyze, and visualize financial data from various document types. Built with a modern serverless architecture using Next.js, Vercel, and Supabase.

## Features

- **Document Upload**: Upload and process PDF, Excel, and CSV files
- **Financial Data Extraction**: Automatically extract ISINs, financial metrics, and key data
- **Portfolio Analysis**: Analyze investment portfolios with advanced metrics
- **AI Agents**: Intelligent agents for document analysis and insights
- **Data Visualization**: Interactive charts and dashboards
- **Multi-tenant Architecture**: Secure isolation of client data
- **Serverless Architecture**: Fully serverless deployment on Vercel
- **Google ADK Integration**: Agent Development Kit for advanced AI capabilities
- **Advanced OCR**: Hebrew language support with enhanced accuracy
- **Document Integration**: Combine data from multiple financial documents
- **Security & Compliance**: GDPR compliance, data encryption, and audit logging
- **Performance Optimization**: Caching and monitoring for optimal performance

## Tech Stack

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
