// Type definitions for the FinDoc application

// User and authentication types
export interface User {
  id: string;
  email: string;
  fullName?: string;
  avatarUrl?: string;
  organizationId?: string;
  role: 'user' | 'admin' | 'owner';
  createdAt: string;
  updatedAt: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: 'free' | 'pro' | 'enterprise';
  subscriptionStatus: 'active' | 'inactive' | 'trial';
  subscriptionId?: string;
  createdAt: string;
  updatedAt: string;
}

// Document types
export interface Document {
  id: string;
  organizationId: string;
  title: string;
  description?: string;
  filePath: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  content?: string;
  metadata?: Record<string, any>;
  tags: string[];
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

export interface DocumentUploadOptions {
  title?: string;
  description?: string;
  tags?: string[];
  processingOptions?: {
    extractTables?: boolean;
    detectHeaders?: boolean;
    sheetNames?: string[] | 'all';
    convertFormulas?: boolean;
    ocrEnabled?: boolean;
    extractText?: boolean;
    extractMetadata?: boolean;
  };
}

// Financial data types
export interface FinancialData {
  id: string;
  documentId?: string;
  organizationId: string;
  dataType: string;
  value: any;
  createdAt: string;
  updatedAt: string;
}

export interface ISIN {
  id: string;
  organizationId: string;
  documentId?: string;
  isin: string;
  description?: string;
  value?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Portfolio {
  id?: string;
  name: string;
  organizationId?: string;
  userId?: string;
  holdings: PortfolioHolding[];
  performanceData?: {
    startValue: number;
    currentValue: number;
    startDate: string;
    currentDate: string;
  };
  riskData?: {
    volatility: number;
    sharpeRatio: number;
    maxDrawdown: number;
    beta: number;
    alpha: number;
  };
  createdAt?: string;
  updatedAt?: string;
}

export interface PortfolioHolding {
  id?: string;
  portfolioId?: string;
  isin: string;
  name: string;
  quantity: number;
  price: number;
  value: number;
  currency: string;
  assetClass?: string;
  sector?: string;
  region?: string;
  costBasis?: number;
  purchaseDate?: string;
  lastUpdated?: string;
}

export interface PortfolioSummary {
  totalValue: number;
  assetAllocation: AssetAllocation;
  performanceMetrics: PerformanceMetrics;
  riskMetrics: RiskMetrics;
  lastUpdated: string;
}

export interface AssetAllocation {
  assetClass: AllocationItem[];
  sector: AllocationItem[];
  region: AllocationItem[];
}

export interface AllocationItem {
  name: string;
  value: number;
  percentage: number;
}

export interface PerformanceMetrics {
  absoluteReturn: number;
  percentageReturn: number;
  annualizedReturn: number;
  startDate: string;
  currentDate: string;
}

export interface RiskMetrics {
  volatility: number;
  sharpeRatio: number;
  maxDrawdown: number;
  beta: number;
  alpha: number;
}

export interface HistoricalPerformance {
  dates: string[];
  values: number[];
}

export interface PortfolioComparison {
  dates: string[];
  portfolio: number[];
  benchmark: number[];
  benchmarkName: string;
}

// Export types
export type ExportFormat = 'csv' | 'excel' | 'json' | 'pdf';

export interface ExportOptions {
  includeMetadata?: boolean;
  includeContent?: boolean;
  dateFormat?: string;
  numberFormat?: string;
  fileName?: string;
  sheetName?: string;
}

// Report types
export type ReportTemplate = 'standard' | 'performance' | 'allocation' | 'risk';

export interface ReportConfig {
  timeframe?: '1M' | '3M' | '6M' | '1Y' | '5Y';
  includeBenchmark?: boolean;
  benchmark?: string;
  includeHoldings?: boolean;
  includeCharts?: boolean;
  customTitle?: string;
  customLogo?: string;
  customFooter?: string;
  customColors?: string[];
}

export interface ReportSchedule {
  id?: string;
  name: string;
  type: 'portfolio' | 'document';
  portfolioId?: string;
  documentId?: string;
  template: ReportTemplate;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annually';
  nextRunDate: string;
  recipients: string[];
  config?: ReportConfig;
  createdAt?: string;
  updatedAt?: string;
}

// Agent types
export interface Agent {
  id: string | number;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'configuring' | 'error';
  capabilities: string[];
}

export interface AgentMessage {
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
}

export interface AgentChatRequest {
  agentId: string | number;
  message: string;
  documentId?: string | number;
}

// API key types
export interface ApiKey {
  id: string;
  organizationId: string;
  name: string;
  keyType: string;
  keyValue: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

// Settings types
export interface Settings {
  general: {
    theme: 'light' | 'dark' | 'system';
    language: string;
    dateFormat: string;
    timezone: string;
  };
  notifications: {
    emailNotifications: boolean;
    documentProcessed: boolean;
    newAnalysisAvailable: boolean;
    securityAlerts: boolean;
  };
  privacy: {
    shareAnalytics: boolean;
    storeDocuments: boolean;
    documentRetention: '30days' | '90days' | '1year' | 'forever';
  };
  display: {
    compactView: boolean;
    showTags: boolean;
    defaultView: 'grid' | 'list' | 'compact';
  };
}
