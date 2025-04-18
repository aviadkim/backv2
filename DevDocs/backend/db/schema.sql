-- FinDoc Database Schema

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
  id SERIAL PRIMARY KEY,
  job_id UUID NOT NULL,
  document_type VARCHAR(50) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  processed_at TIMESTAMP WITH TIME ZONE NOT NULL,
  language VARCHAR(10),
  status VARCHAR(20) NOT NULL,
  validation_errors INTEGER NOT NULL DEFAULT 0,
  validation_warnings INTEGER NOT NULL DEFAULT 0,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document text table
CREATE TABLE IF NOT EXISTS document_text (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  text_content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document tables table
CREATE TABLE IF NOT EXISTS document_tables (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  table_id VARCHAR(100) NOT NULL,
  page INTEGER,
  extraction_method VARCHAR(50) NOT NULL,
  table_number INTEGER,
  headers JSONB NOT NULL,
  rows JSONB NOT NULL,
  accuracy FLOAT,
  bbox JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document ISINs table
CREATE TABLE IF NOT EXISTS document_isins (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  isin VARCHAR(12) NOT NULL,
  name VARCHAR(255),
  quantity FLOAT,
  value FLOAT,
  source VARCHAR(50),
  security_type VARCHAR(50),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  portfolio_value FLOAT,
  currency VARCHAR(3),
  asset_allocation JSONB,
  performance JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Securities table
CREATE TABLE IF NOT EXISTS securities (
  id SERIAL PRIMARY KEY,
  portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  isin VARCHAR(12) NOT NULL,
  name VARCHAR(255),
  quantity FLOAT,
  price FLOAT,
  value FLOAT,
  currency VARCHAR(3),
  security_type VARCHAR(50),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Processing errors table
CREATE TABLE IF NOT EXISTS processing_errors (
  id SERIAL PRIMARY KEY,
  job_id UUID NOT NULL,
  error_message TEXT NOT NULL,
  error_stack TEXT,
  error_time TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_documents_job_id ON documents(job_id);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_document_tables_document_id ON document_tables(document_id);
CREATE INDEX IF NOT EXISTS idx_document_isins_document_id ON document_isins(document_id);
CREATE INDEX IF NOT EXISTS idx_document_isins_isin ON document_isins(isin);
CREATE INDEX IF NOT EXISTS idx_portfolios_document_id ON portfolios(document_id);
CREATE INDEX IF NOT EXISTS idx_securities_portfolio_id ON securities(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_securities_document_id ON securities(document_id);
CREATE INDEX IF NOT EXISTS idx_securities_isin ON securities(isin);
CREATE INDEX IF NOT EXISTS idx_processing_errors_job_id ON processing_errors(job_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to update updated_at timestamp
CREATE TRIGGER update_documents_updated_at
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolios_updated_at
BEFORE UPDATE ON portfolios
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_securities_updated_at
BEFORE UPDATE ON securities
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
