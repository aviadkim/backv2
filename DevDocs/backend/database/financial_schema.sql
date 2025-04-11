-- Financial Data Schema for Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations (for multi-tenancy)
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User profiles with organization relationship
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users,
  organization_id UUID REFERENCES organizations,
  first_name TEXT,
  last_name TEXT,
  email TEXT,
  role TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  file_path TEXT,
  file_type TEXT,
  file_size INTEGER,
  status TEXT DEFAULT 'pending',
  processing_results JSONB,
  created_by UUID REFERENCES profiles,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Securities table
CREATE TABLE securities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations NOT NULL,
  isin TEXT,
  cusip TEXT,
  ticker TEXT,
  name TEXT NOT NULL,
  description TEXT,
  asset_class TEXT,
  sector TEXT,
  industry TEXT,
  region TEXT,
  country TEXT,
  currency TEXT,
  exchange TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(organization_id, isin)
);

-- Security prices
CREATE TABLE security_prices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  security_id UUID REFERENCES securities NOT NULL,
  price DECIMAL NOT NULL,
  currency TEXT,
  date DATE NOT NULL,
  source TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(security_id, date)
);

-- Portfolios
CREATE TABLE portfolios (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  base_currency TEXT,
  created_by UUID REFERENCES profiles,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio holdings
CREATE TABLE portfolio_holdings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  portfolio_id UUID REFERENCES portfolios NOT NULL,
  security_id UUID REFERENCES securities NOT NULL,
  quantity DECIMAL,
  cost_per_unit DECIMAL,
  cost_currency TEXT,
  purchase_date DATE,
  notes TEXT,
  source_document_id UUID REFERENCES documents,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(portfolio_id, security_id)
);

-- Portfolio transactions
CREATE TABLE portfolio_transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  portfolio_id UUID REFERENCES portfolios NOT NULL,
  security_id UUID REFERENCES securities,
  transaction_type TEXT NOT NULL, -- buy, sell, dividend, interest, fee, transfer
  transaction_date DATE NOT NULL,
  quantity DECIMAL,
  price DECIMAL,
  amount DECIMAL NOT NULL,
  currency TEXT,
  fees DECIMAL,
  taxes DECIMAL,
  notes TEXT,
  source_document_id UUID REFERENCES documents,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial statements
CREATE TABLE financial_statements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations NOT NULL,
  statement_type TEXT NOT NULL, -- income_statement, balance_sheet, cash_flow
  period_start DATE,
  period_end DATE,
  as_of_date DATE,
  currency TEXT,
  source_document_id UUID REFERENCES documents,
  data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial metrics extracted from documents
CREATE TABLE financial_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations NOT NULL,
  document_id UUID REFERENCES documents NOT NULL,
  metric_type TEXT NOT NULL, -- profitability, liquidity, solvency, valuation, growth, efficiency
  metric_name TEXT NOT NULL,
  value DECIMAL,
  currency TEXT,
  period_start DATE,
  period_end DATE,
  context TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reports
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations NOT NULL,
  report_type TEXT NOT NULL, -- portfolio, profit_loss, balance_sheet, cash_flow, financial_metrics
  title TEXT NOT NULL,
  description TEXT,
  parameters JSONB,
  result_data JSONB,
  file_path TEXT,
  created_by UUID REFERENCES profiles,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI analysis and recommendations
CREATE TABLE ai_analysis (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations NOT NULL,
  analysis_type TEXT NOT NULL, -- portfolio_recommendation, financial_insight, risk_assessment
  target_id UUID, -- Can reference portfolio_id, document_id, etc.
  target_type TEXT, -- portfolio, document, financial_statement
  analysis_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row-Level Security Policies

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE securities ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_statements ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_analysis ENABLE ROW LEVEL SECURITY;

-- Organizations policy
CREATE POLICY "Users can only access their organization"
ON organizations
USING (id IN (
  SELECT organization_id FROM profiles WHERE id = auth.uid()
));

-- Profiles policy
CREATE POLICY "Users can only view profiles in their organization"
ON profiles
USING (organization_id IN (
  SELECT organization_id FROM profiles WHERE id = auth.uid()
));

CREATE POLICY "Users can only update their own profile"
ON profiles
FOR UPDATE
USING (id = auth.uid());

-- Documents policy
CREATE POLICY "Users can only access their organization's documents"
ON documents
USING (organization_id IN (
  SELECT organization_id FROM profiles WHERE id = auth.uid()
));

-- Securities policy
CREATE POLICY "Users can only access their organization's securities"
ON securities
USING (organization_id IN (
  SELECT organization_id FROM profiles WHERE id = auth.uid()
));

-- Security prices policy
CREATE POLICY "Users can only access prices for their organization's securities"
ON security_prices
USING (security_id IN (
  SELECT id FROM securities WHERE organization_id IN (
    SELECT organization_id FROM profiles WHERE id = auth.uid()
  )
));

-- Portfolios policy
CREATE POLICY "Users can only access their organization's portfolios"
ON portfolios
USING (organization_id IN (
  SELECT organization_id FROM profiles WHERE id = auth.uid()
));

-- Portfolio holdings policy
CREATE POLICY "Users can only access holdings for their organization's portfolios"
ON portfolio_holdings
USING (portfolio_id IN (
  SELECT id FROM portfolios WHERE organization_id IN (
    SELECT organization_id FROM profiles WHERE id = auth.uid()
  )
));

-- Portfolio transactions policy
CREATE POLICY "Users can only access transactions for their organization's portfolios"
ON portfolio_transactions
USING (portfolio_id IN (
  SELECT id FROM portfolios WHERE organization_id IN (
    SELECT organization_id FROM profiles WHERE id = auth.uid()
  )
));

-- Financial statements policy
CREATE POLICY "Users can only access their organization's financial statements"
ON financial_statements
USING (organization_id IN (
  SELECT organization_id FROM profiles WHERE id = auth.uid()
));

-- Financial metrics policy
CREATE POLICY "Users can only access their organization's financial metrics"
ON financial_metrics
USING (organization_id IN (
  SELECT organization_id FROM profiles WHERE id = auth.uid()
));

-- Reports policy
CREATE POLICY "Users can only access their organization's reports"
ON reports
USING (organization_id IN (
  SELECT organization_id FROM profiles WHERE id = auth.uid()
));

-- AI analysis policy
CREATE POLICY "Users can only access their organization's AI analysis"
ON ai_analysis
USING (organization_id IN (
  SELECT organization_id FROM profiles WHERE id = auth.uid()
));

-- Create indexes for performance
CREATE INDEX idx_documents_organization ON documents(organization_id);
CREATE INDEX idx_securities_organization ON securities(organization_id);
CREATE INDEX idx_securities_isin ON securities(isin);
CREATE INDEX idx_security_prices_security ON security_prices(security_id);
CREATE INDEX idx_security_prices_date ON security_prices(date);
CREATE INDEX idx_portfolios_organization ON portfolios(organization_id);
CREATE INDEX idx_portfolio_holdings_portfolio ON portfolio_holdings(portfolio_id);
CREATE INDEX idx_portfolio_holdings_security ON portfolio_holdings(security_id);
CREATE INDEX idx_portfolio_transactions_portfolio ON portfolio_transactions(portfolio_id);
CREATE INDEX idx_portfolio_transactions_security ON portfolio_transactions(security_id);
CREATE INDEX idx_portfolio_transactions_date ON portfolio_transactions(transaction_date);
CREATE INDEX idx_financial_statements_organization ON financial_statements(organization_id);
CREATE INDEX idx_financial_statements_type ON financial_statements(statement_type);
CREATE INDEX idx_financial_metrics_organization ON financial_metrics(organization_id);
CREATE INDEX idx_financial_metrics_document ON financial_metrics(document_id);
CREATE INDEX idx_reports_organization ON reports(organization_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_ai_analysis_organization ON ai_analysis(organization_id);
CREATE INDEX idx_ai_analysis_target ON ai_analysis(target_id, target_type);
