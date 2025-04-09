# FinDoc Developer Guide

This guide provides instructions for developers working on the FinDoc project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment](#development-environment)
3. [Project Structure](#project-structure)
4. [MCP Architecture](#mcp-architecture)
5. [Working with Supabase](#working-with-supabase)
6. [Authentication](#authentication)
7. [Document Processing](#document-processing)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Best Practices](#best-practices)

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.8+
- Git
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aviadkim/backv2.git
   cd backv2
   ```

2. Install frontend dependencies:
   ```bash
   cd DevDocs/frontend
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env.local` file in `DevDocs/frontend/` based on `.env.example`
   - Add your Supabase URL and anon key

5. Start the development server:
   ```bash
   cd ../..
   ./run-findoc-enhanced.ps1
   ```

6. Open [http://localhost:3002](http://localhost:3002) in your browser.

## Development Environment

### Editor Setup

We recommend using Visual Studio Code with the following extensions:
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Python
- GitLens

### MCP Server

The MCP Server helps generate components following the Model-Controller-Provider pattern:

1. Install MCP tools:
   ```bash
   ./install-mcp-tools.ps1
   ```

2. Start the MCP Server:
   ```bash
   ./start-mcp-server.ps1
   ```

3. Generate components:
   ```bash
   mcp generate-all -p findoc -n Feature -d "Feature description"
   ```

## Project Structure

```
DevDocs/
├── frontend/              # Next.js frontend
│   ├── components/        # Reusable React components
│   ├── controllers/       # Business logic
│   ├── lib/               # Utility functions
│   ├── models/            # Data models and types
│   ├── pages/             # Next.js pages
│   ├── providers/         # Context providers
│   ├── public/            # Static assets
│   ├── repositories/      # Data access layer
│   └── styles/            # CSS and styling
│
├── backend/               # Flask backend
│   ├── agents/            # AI agents
│   ├── document_processor.py  # Document processing
│   ├── app.py             # Main Flask application
│   └── requirements.txt   # Python dependencies
│
├── supabase/              # Supabase configuration
│   └── schema.sql         # Database schema
│
└── MCP/                   # MCP Server and tools
    ├── augment-mcp-server/  # MCP Server
    └── augment-mcp-client/  # MCP Client
```

## MCP Architecture

The MCP (Model-Controller-Provider) architecture separates concerns:

### Models

Models define data structures and validation rules:

```typescript
// Create a new model
mcp generate -p findoc -t model -n User -d "User model for authentication"
```

### Controllers

Controllers implement business logic:

```typescript
// Create a new controller
mcp generate -p findoc -t controller -n Document -d "Document management"
```

### Providers

Providers manage state and provide data access to components:

```typescript
// Create a new provider
mcp generate -p findoc -t provider -n Portfolio -d "Portfolio data provider"
```

### Repositories

Repositories handle data access:

```typescript
// Create a new repository
mcp generate -p findoc -t repository -n ISIN -d "ISIN data access"
```

## Working with Supabase

### Supabase Client

Use the Supabase client to interact with the database:

```typescript
import getSupabaseClient from '../lib/supabaseClient';

const fetchData = async () => {
  const supabase = getSupabaseClient();
  if (!supabase) return [];
  
  const { data, error } = await supabase
    .from('documents')
    .select('*')
    .order('created_at', { ascending: false });
  
  if (error) {
    console.error('Error fetching data:', error);
    return [];
  }
  
  return data;
};
```

### Row-Level Security

All tables have Row-Level Security (RLS) policies to ensure data isolation:

```sql
-- Example RLS policy
CREATE POLICY "Documents are accessible by organization members"
ON documents FOR SELECT
USING (
  organization_id IN (
    SELECT organization_id FROM profiles
    WHERE id = auth.uid()
  )
);
```

### Storage

Use Supabase Storage for file storage:

```typescript
const uploadFile = async (file: File, path: string) => {
  const supabase = getSupabaseClient();
  if (!supabase) throw new Error('Supabase client not available');
  
  const { data, error } = await supabase
    .storage
    .from('documents')
    .upload(path, file);
  
  if (error) throw error;
  
  return data.path;
};
```

## Authentication

### Using the Auth Provider

Wrap your application with the `AuthProvider`:

```tsx
// _app.js
import { AuthProvider } from '../providers/AuthProvider';

function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  );
}
```

### Accessing Auth Context

Use the `useAuth` hook to access authentication functions:

```tsx
import { useAuth } from '../providers/AuthProvider';

const ProfilePage = () => {
  const { user, updateProfile, signOut } = useAuth();
  
  // Use auth functions
};
```

### Protected Routes

Use the `withProtectedRoute` HOC to protect pages:

```tsx
import withProtectedRoute from '../components/ProtectedRoute';

const DashboardPage = () => {
  // Dashboard content
};

export default withProtectedRoute(DashboardPage);
```

## Document Processing

### Uploading Documents

Use the `DocumentProvider` to upload documents:

```tsx
import { useDocument } from '../providers/DocumentProvider';

const UploadPage = () => {
  const { uploadDocument } = useDocument();
  
  const handleUpload = async (file) => {
    try {
      await uploadDocument(file, {
        title: 'My Document',
        tags: ['financial', 'report']
      });
    } catch (error) {
      console.error('Upload error:', error);
    }
  };
};
```

### Processing Documents

The backend handles document processing:

```python
# Process a document
result = document_processor.process_document(file_path, doc_type, processing_options)
```

## Testing

### Frontend Tests

Run frontend tests:

```bash
cd DevDocs/frontend
npm test
```

### Backend Tests

Run backend tests:

```bash
cd DevDocs/backend
python -m pytest
```

### End-to-End Tests

Run end-to-end tests:

```bash
cd DevDocs/frontend
npm run test:e2e
```

## Deployment

### Vercel Deployment

Deploy to Vercel:

1. Push your changes to GitHub
2. Vercel will automatically deploy the changes
3. Check the deployment status in the Vercel dashboard

### Manual Deployment

Deploy manually:

```bash
cd DevDocs/frontend
npm run build
vercel --prod
```

## Best Practices

### Code Style

- Follow the ESLint and Prettier configuration
- Use TypeScript for type safety
- Write meaningful comments
- Use descriptive variable and function names

### Git Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "Add my feature"
   ```

3. Push to GitHub:
   ```bash
   git push origin feature/my-feature
   ```

4. Create a pull request on GitHub

### Documentation

- Document all new features and changes
- Update README.md when necessary
- Add JSDoc comments to functions and components
- Keep the development roadmap up to date
