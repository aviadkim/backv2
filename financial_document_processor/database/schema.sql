-- Financial Document Processor Database Schema

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_path TEXT,
    file_size INTEGER,
    content_type TEXT,
    page_count INTEGER,
    title TEXT,
    author TEXT,
    creation_date TIMESTAMP,
    modification_date TIMESTAMP,
    document_date TIMESTAMP,
    document_type TEXT,
    processing_status TEXT DEFAULT 'pending',
    extraction_date TIMESTAMP DEFAULT NOW(),
    extraction_method TEXT,
    extraction_version TEXT,
    risk_profile TEXT,
    currency TEXT,
    validation_status TEXT,
    validation_issues JSONB,
    metadata JSONB
);

-- Securities table
CREATE TABLE IF NOT EXISTS securities (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    isin TEXT,
    cusip TEXT,
    ticker TEXT,
    name TEXT,
    description TEXT,
    security_type TEXT,
    asset_class TEXT,
    valuation FLOAT,
    price FLOAT,
    quantity FLOAT,
    currency TEXT,
    coupon_rate FLOAT,
    maturity_date TIMESTAMP,
    extraction_method TEXT,
    confidence_score FLOAT,
    validation_status TEXT,
    validation_issues JSONB,
    metadata JSONB
);

-- Create index on ISIN for faster lookups
CREATE INDEX IF NOT EXISTS idx_securities_isin ON securities(isin);

-- Create index on document_id for faster joins
CREATE INDEX IF NOT EXISTS idx_securities_document_id ON securities(document_id);

-- Portfolio values table
CREATE TABLE IF NOT EXISTS portfolio_values (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    value FLOAT NOT NULL,
    currency TEXT,
    value_date TIMESTAMP,
    extraction_method TEXT,
    confidence_score FLOAT,
    validation_status TEXT,
    validation_issues JSONB,
    metadata JSONB
);

-- Create index on document_id for faster joins
CREATE INDEX IF NOT EXISTS idx_portfolio_values_document_id ON portfolio_values(document_id);

-- Asset allocations table
CREATE TABLE IF NOT EXISTS asset_allocations (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    asset_class TEXT NOT NULL,
    value FLOAT,
    percentage FLOAT,
    currency TEXT,
    parent_id INTEGER REFERENCES asset_allocations(id),
    extraction_method TEXT,
    confidence_score FLOAT,
    validation_status TEXT,
    validation_issues JSONB,
    metadata JSONB
);

-- Create index on document_id for faster joins
CREATE INDEX IF NOT EXISTS idx_asset_allocations_document_id ON asset_allocations(document_id);

-- Create index on parent_id for hierarchical queries
CREATE INDEX IF NOT EXISTS idx_asset_allocations_parent_id ON asset_allocations(parent_id);

-- Raw text table
CREATE TABLE IF NOT EXISTS raw_texts (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE UNIQUE,
    content TEXT,
    extraction_method TEXT,
    metadata JSONB
);

-- Create index on document_id for faster joins
CREATE INDEX IF NOT EXISTS idx_raw_texts_document_id ON raw_texts(document_id);

-- Document tables table
CREATE TABLE IF NOT EXISTS document_tables (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER,
    table_number INTEGER,
    extraction_method TEXT,
    headers JSONB,
    data JSONB,
    accuracy FLOAT,
    metadata JSONB
);

-- Create index on document_id for faster joins
CREATE INDEX IF NOT EXISTS idx_document_tables_document_id ON document_tables(document_id);

-- Create index on page_number for faster lookups
CREATE INDEX IF NOT EXISTS idx_document_tables_page_number ON document_tables(page_number);

-- Financial entities table
CREATE TABLE IF NOT EXISTS financial_entities (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL,
    value TEXT,
    position INTEGER,
    context TEXT,
    confidence_score FLOAT,
    metadata JSONB
);

-- Create index on document_id for faster joins
CREATE INDEX IF NOT EXISTS idx_financial_entities_document_id ON financial_entities(document_id);

-- Create index on entity_type for faster lookups
CREATE INDEX IF NOT EXISTS idx_financial_entities_entity_type ON financial_entities(entity_type);

-- Validation results table
CREATE TABLE IF NOT EXISTS validation_results (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    validation_date TIMESTAMP DEFAULT NOW(),
    valid BOOLEAN,
    issues JSONB,
    metadata JSONB
);

-- Create index on document_id for faster joins
CREATE INDEX IF NOT EXISTS idx_validation_results_document_id ON validation_results(document_id);

-- Document comparisons table
CREATE TABLE IF NOT EXISTS document_comparisons (
    id SERIAL PRIMARY KEY,
    document_id_1 INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    document_id_2 INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    comparison_date TIMESTAMP DEFAULT NOW(),
    similarity_score FLOAT,
    differences JSONB,
    metadata JSONB
);

-- Create index on document_id_1 for faster joins
CREATE INDEX IF NOT EXISTS idx_document_comparisons_document_id_1 ON document_comparisons(document_id_1);

-- Create index on document_id_2 for faster joins
CREATE INDEX IF NOT EXISTS idx_document_comparisons_document_id_2 ON document_comparisons(document_id_2);

-- Document queries table
CREATE TABLE IF NOT EXISTS document_queries (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    answer TEXT,
    query_date TIMESTAMP DEFAULT NOW(),
    model TEXT,
    confidence_score FLOAT,
    metadata JSONB
);

-- Create index on document_id for faster joins
CREATE INDEX IF NOT EXISTS idx_document_queries_document_id ON document_queries(document_id);

-- Enable Row Level Security (RLS)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE securities ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_values ENABLE ROW LEVEL SECURITY;
ALTER TABLE asset_allocations ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw_texts ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_tables ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE validation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_comparisons ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_queries ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY "Allow authenticated users to read documents" ON documents
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read securities" ON securities
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read portfolio_values" ON portfolio_values
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read asset_allocations" ON asset_allocations
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read raw_texts" ON raw_texts
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read document_tables" ON document_tables
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read financial_entities" ON financial_entities
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read validation_results" ON validation_results
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read document_comparisons" ON document_comparisons
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read document_queries" ON document_queries
    FOR SELECT USING (auth.role() = 'authenticated');

-- Create policies for service role
CREATE POLICY "Allow service role to manage documents" ON documents
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role to manage securities" ON securities
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role to manage portfolio_values" ON portfolio_values
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role to manage asset_allocations" ON asset_allocations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role to manage raw_texts" ON raw_texts
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role to manage document_tables" ON document_tables
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role to manage financial_entities" ON financial_entities
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role to manage validation_results" ON validation_results
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role to manage document_comparisons" ON document_comparisons
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role to manage document_queries" ON document_queries
    FOR ALL USING (auth.role() = 'service_role');
