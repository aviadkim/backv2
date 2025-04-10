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

## Tech Stack

- **Frontend**: Next.js, React, TailwindCSS
- **API**: Next.js API Routes (serverless functions)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Deployment**: Vercel
- **AI**: OpenRouter API, Google ADK
- **Authentication**: Supabase Auth

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

This project is configured for deployment on Vercel with Supabase as the database and storage solution.

See [VERCEL_SUPABASE_DEPLOYMENT.md](VERCEL_SUPABASE_DEPLOYMENT.md) for detailed deployment instructions.

## Development Roadmap

See [ROADMAP.md](ROADMAP.md) for the detailed development plan.

## Database Schema

The database schema is defined in [supabase/schema.sql](supabase/schema.sql) and includes tables for:

- Users (profiles)
- Organizations
- Documents
- Financial data
- ISINs
- API keys

## License

This project is proprietary and confidential.

## Contact

For questions or support, please contact the development team.
