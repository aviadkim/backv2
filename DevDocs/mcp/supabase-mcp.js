/**
 * Supabase MCP - Model, Controller, Provider pattern for Supabase integration
 * This file helps configure and manage Supabase connections
 */

// Model - Configuration data
const supabaseConfig = {
  projectUrl: process.env.NEXT_PUBLIC_SUPABASE_URL,
  anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  serviceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY,
  tables: [
    'profiles',
    'organizations',
    'documents',
    'financial_data',
    'isins',
    'api_keys'
  ],
  storageBuckets: [
    'documents'
  ]
};

// Controller - Functions to manage Supabase
const supabaseController = {
  getConfig() {
    return supabaseConfig;
  },
  
  validateConfig() {
    // Check if all required fields are present
    if (!supabaseConfig.projectUrl || !supabaseConfig.anonKey) {
      throw new Error('Missing required Supabase configuration');
    }
    
    return true;
  },
  
  getClientConfig() {
    return {
      supabaseUrl: supabaseConfig.projectUrl,
      supabaseKey: supabaseConfig.anonKey
    };
  },
  
  getServiceClientConfig() {
    return {
      supabaseUrl: supabaseConfig.projectUrl,
      supabaseKey: supabaseConfig.serviceRoleKey
    };
  }
};

// Provider - Interface for external systems
const supabaseProvider = {
  getClientConfig() {
    supabaseController.validateConfig();
    return supabaseController.getClientConfig();
  },
  
  getServiceClientConfig() {
    supabaseController.validateConfig();
    return supabaseController.getServiceClientConfig();
  },
  
  getTables() {
    return supabaseConfig.tables;
  },
  
  getStorageBuckets() {
    return supabaseConfig.storageBuckets;
  }
};

module.exports = {
  supabaseConfig,
  supabaseController,
  supabaseProvider
};
