#!/usr/bin/env node

/**
 * Health check script for FinDoc Analyzer
 * 
 * This script checks if the application is running properly by:
 * 1. Checking if the backend server is responding
 * 2. Checking if the frontend server is responding
 * 3. Checking if the database connection is working
 */

const http = require('http');
const { createClient } = require('@supabase/supabase-js');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3001';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3002';
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;

// Check if backend is running
function checkBackend() {
  return new Promise((resolve, reject) => {
    http.get(`${BACKEND_URL}/api/health`, (res) => {
      if (res.statusCode === 200) {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            if (response.status === 'ok') {
              resolve(true);
            } else {
              reject(new Error('Backend health check failed'));
            }
          } catch (error) {
            reject(new Error('Invalid response from backend'));
          }
        });
      } else {
        reject(new Error(`Backend returned status code ${res.statusCode}`));
      }
    }).on('error', (error) => {
      reject(new Error(`Backend connection error: ${error.message}`));
    });
  });
}

// Check if frontend is running
function checkFrontend() {
  return new Promise((resolve, reject) => {
    http.get(FRONTEND_URL, (res) => {
      if (res.statusCode === 200) {
        resolve(true);
      } else {
        reject(new Error(`Frontend returned status code ${res.statusCode}`));
      }
    }).on('error', (error) => {
      reject(new Error(`Frontend connection error: ${error.message}`));
    });
  });
}

// Check if database connection is working
function checkDatabase() {
  return new Promise((resolve, reject) => {
    if (!SUPABASE_URL || !SUPABASE_KEY) {
      console.warn('Supabase credentials not provided, skipping database check');
      resolve(true);
      return;
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
    
    supabase.from('health_check')
      .select('count')
      .limit(1)
      .then(() => {
        resolve(true);
      })
      .catch((error) => {
        reject(new Error(`Database connection error: ${error.message}`));
      });
  });
}

// Run all checks
async function runHealthCheck() {
  try {
    await checkBackend();
    await checkFrontend();
    await checkDatabase();
    console.log('Health check passed');
    process.exit(0);
  } catch (error) {
    console.error('Health check failed:', error.message);
    process.exit(1);
  }
}

// Run the health check
runHealthCheck();
