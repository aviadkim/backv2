-- Initial Schema Migration for FinDoc Analyzer
-- This migration creates the initial database schema for the application

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_login TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT TRUE,
  preferences JSONB DEFAULT '{}'::jsonb
);

-- Create organizations table
CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  settings JSONB DEFAULT '{}'::jsonb
);

-- Create organization_users table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS organization_users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL DEFAULT 'member',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(organization_id, user_id)
);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  file_path VARCHAR(255) NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  file_size INTEGER NOT NULL,
  content_type VARCHAR(100) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',
  processing_error TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create document_data table
CREATE TABLE IF NOT EXISTS document_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  data_type VARCHAR(50) NOT NULL,
  content JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create financial_entities table
CREATE TABLE IF NOT EXISTS financial_entities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  isin VARCHAR(12),
  entity_type VARCHAR(50) NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(organization_id, isin) WHERE isin IS NOT NULL
);

-- Create financial_data table
CREATE TABLE IF NOT EXISTS financial_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  financial_entity_id UUID NOT NULL REFERENCES financial_entities(id) ON DELETE CASCADE,
  data_type VARCHAR(50) NOT NULL,
  value NUMERIC(19, 4) NOT NULL,
  currency VARCHAR(3) NOT NULL,
  date DATE NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create api_keys table
CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  key VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  permissions JSONB DEFAULT '[]'::jsonb,
  expires_at TIMESTAMP WITH TIME ZONE,
  last_used_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  active BOOLEAN DEFAULT TRUE
);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
  action VARCHAR(100) NOT NULL,
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID,
  details JSONB DEFAULT '{}'::jsonb,
  ip_address VARCHAR(45),
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create health_check table
CREATE TABLE IF NOT EXISTS health_check (
  id SERIAL PRIMARY KEY,
  count INTEGER DEFAULT 0,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert initial health check record
INSERT INTO health_check (count) VALUES (0) ON CONFLICT DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_documents_organization_id ON documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_document_data_document_id ON document_data(document_id);
CREATE INDEX IF NOT EXISTS idx_financial_entities_organization_id ON financial_entities(organization_id);
CREATE INDEX IF NOT EXISTS idx_financial_entities_isin ON financial_entities(isin);
CREATE INDEX IF NOT EXISTS idx_financial_data_document_id ON financial_data(document_id);
CREATE INDEX IF NOT EXISTS idx_financial_data_financial_entity_id ON financial_data(financial_entity_id);
CREATE INDEX IF NOT EXISTS idx_financial_data_date ON financial_data(date);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_organization_id ON audit_logs(organization_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Create RLS policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Create functions for RLS
CREATE OR REPLACE FUNCTION is_member_of_organization(org_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM organization_users
    WHERE organization_id = org_id
    AND user_id = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create RLS policies for users
CREATE POLICY users_select ON users
  FOR SELECT USING (
    auth.uid() = id OR
    auth.role() = 'admin' OR
    EXISTS (
      SELECT 1 FROM organization_users
      WHERE user_id = users.id
      AND organization_id IN (
        SELECT organization_id FROM organization_users
        WHERE user_id = auth.uid()
      )
    )
  );

CREATE POLICY users_insert ON users
  FOR INSERT WITH CHECK (
    auth.role() = 'admin'
  );

CREATE POLICY users_update ON users
  FOR UPDATE USING (
    auth.uid() = id OR
    auth.role() = 'admin'
  );

CREATE POLICY users_delete ON users
  FOR DELETE USING (
    auth.role() = 'admin'
  );

-- Create RLS policies for organizations
CREATE POLICY organizations_select ON organizations
  FOR SELECT USING (
    is_member_of_organization(id) OR
    auth.role() = 'admin'
  );

CREATE POLICY organizations_insert ON organizations
  FOR INSERT WITH CHECK (
    auth.role() = 'admin'
  );

CREATE POLICY organizations_update ON organizations
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM organization_users
      WHERE organization_id = organizations.id
      AND user_id = auth.uid()
      AND role = 'admin'
    ) OR
    auth.role() = 'admin'
  );

CREATE POLICY organizations_delete ON organizations
  FOR DELETE USING (
    auth.role() = 'admin'
  );

-- Create RLS policies for organization_users
CREATE POLICY organization_users_select ON organization_users
  FOR SELECT USING (
    user_id = auth.uid() OR
    is_member_of_organization(organization_id) OR
    auth.role() = 'admin'
  );

CREATE POLICY organization_users_insert ON organization_users
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM organization_users
      WHERE organization_id = organization_users.organization_id
      AND user_id = auth.uid()
      AND role = 'admin'
    ) OR
    auth.role() = 'admin'
  );

CREATE POLICY organization_users_update ON organization_users
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM organization_users
      WHERE organization_id = organization_users.organization_id
      AND user_id = auth.uid()
      AND role = 'admin'
    ) OR
    auth.role() = 'admin'
  );

CREATE POLICY organization_users_delete ON organization_users
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM organization_users
      WHERE organization_id = organization_users.organization_id
      AND user_id = auth.uid()
      AND role = 'admin'
    ) OR
    auth.role() = 'admin'
  );

-- Create RLS policies for documents
CREATE POLICY documents_select ON documents
  FOR SELECT USING (
    user_id = auth.uid() OR
    is_member_of_organization(organization_id) OR
    auth.role() = 'admin'
  );

CREATE POLICY documents_insert ON documents
  FOR INSERT WITH CHECK (
    is_member_of_organization(organization_id) OR
    auth.role() = 'admin'
  );

CREATE POLICY documents_update ON documents
  FOR UPDATE USING (
    user_id = auth.uid() OR
    is_member_of_organization(organization_id) OR
    auth.role() = 'admin'
  );

CREATE POLICY documents_delete ON documents
  FOR DELETE USING (
    user_id = auth.uid() OR
    EXISTS (
      SELECT 1 FROM organization_users
      WHERE organization_id = documents.organization_id
      AND user_id = auth.uid()
      AND role = 'admin'
    ) OR
    auth.role() = 'admin'
  );

-- Create RLS policies for document_data
CREATE POLICY document_data_select ON document_data
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM documents
      WHERE id = document_data.document_id
      AND (
        user_id = auth.uid() OR
        is_member_of_organization(organization_id) OR
        auth.role() = 'admin'
      )
    )
  );

CREATE POLICY document_data_insert ON document_data
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM documents
      WHERE id = document_data.document_id
      AND (
        user_id = auth.uid() OR
        is_member_of_organization(organization_id) OR
        auth.role() = 'admin'
      )
    )
  );

CREATE POLICY document_data_update ON document_data
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM documents
      WHERE id = document_data.document_id
      AND (
        user_id = auth.uid() OR
        is_member_of_organization(organization_id) OR
        auth.role() = 'admin'
      )
    )
  );

CREATE POLICY document_data_delete ON document_data
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM documents
      WHERE id = document_data.document_id
      AND (
        user_id = auth.uid() OR
        EXISTS (
          SELECT 1 FROM organization_users
          WHERE organization_id = documents.organization_id
          AND user_id = auth.uid()
          AND role = 'admin'
        ) OR
        auth.role() = 'admin'
      )
    )
  );

-- Create RLS policies for financial_entities
CREATE POLICY financial_entities_select ON financial_entities
  FOR SELECT USING (
    is_member_of_organization(organization_id) OR
    auth.role() = 'admin'
  );

CREATE POLICY financial_entities_insert ON financial_entities
  FOR INSERT WITH CHECK (
    is_member_of_organization(organization_id) OR
    auth.role() = 'admin'
  );

CREATE POLICY financial_entities_update ON financial_entities
  FOR UPDATE USING (
    is_member_of_organization(organization_id) OR
    auth.role() = 'admin'
  );

CREATE POLICY financial_entities_delete ON financial_entities
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM organization_users
      WHERE organization_id = financial_entities.organization_id
      AND user_id = auth.uid()
      AND role = 'admin'
    ) OR
    auth.role() = 'admin'
  );

-- Create RLS policies for financial_data
CREATE POLICY financial_data_select ON financial_data
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM documents
      WHERE id = financial_data.document_id
      AND (
        user_id = auth.uid() OR
        is_member_of_organization(organization_id) OR
        auth.role() = 'admin'
      )
    )
  );

CREATE POLICY financial_data_insert ON financial_data
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM documents
      WHERE id = financial_data.document_id
      AND (
        user_id = auth.uid() OR
        is_member_of_organization(organization_id) OR
        auth.role() = 'admin'
      )
    )
  );

CREATE POLICY financial_data_update ON financial_data
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM documents
      WHERE id = financial_data.document_id
      AND (
        user_id = auth.uid() OR
        is_member_of_organization(organization_id) OR
        auth.role() = 'admin'
      )
    )
  );

CREATE POLICY financial_data_delete ON financial_data
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM documents
      WHERE id = financial_data.document_id
      AND (
        user_id = auth.uid() OR
        EXISTS (
          SELECT 1 FROM organization_users
          WHERE organization_id = documents.organization_id
          AND user_id = auth.uid()
          AND role = 'admin'
        ) OR
        auth.role() = 'admin'
      )
    )
  );

-- Create RLS policies for api_keys
CREATE POLICY api_keys_select ON api_keys
  FOR SELECT USING (
    user_id = auth.uid() OR
    auth.role() = 'admin'
  );

CREATE POLICY api_keys_insert ON api_keys
  FOR INSERT WITH CHECK (
    user_id = auth.uid() OR
    auth.role() = 'admin'
  );

CREATE POLICY api_keys_update ON api_keys
  FOR UPDATE USING (
    user_id = auth.uid() OR
    auth.role() = 'admin'
  );

CREATE POLICY api_keys_delete ON api_keys
  FOR DELETE USING (
    user_id = auth.uid() OR
    auth.role() = 'admin'
  );

-- Create RLS policies for audit_logs
CREATE POLICY audit_logs_select ON audit_logs
  FOR SELECT USING (
    user_id = auth.uid() OR
    (
      organization_id IS NOT NULL AND
      is_member_of_organization(organization_id) AND
      EXISTS (
        SELECT 1 FROM organization_users
        WHERE organization_id = audit_logs.organization_id
        AND user_id = auth.uid()
        AND role = 'admin'
      )
    ) OR
    auth.role() = 'admin'
  );

CREATE POLICY audit_logs_insert ON audit_logs
  FOR INSERT WITH CHECK (
    TRUE
  );

-- No update or delete policies for audit_logs as they should be immutable
