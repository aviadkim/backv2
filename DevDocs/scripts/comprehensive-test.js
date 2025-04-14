#!/usr/bin/env node

/**
 * Comprehensive Test Script
 * 
 * This script runs a comprehensive set of tests on the application,
 * identifies issues, and provides guidance on how to fix them.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const chalk = require('chalk');

// Test categories
const testCategories = {
  'build': [
    { id: 'next-build', name: 'Next.js Build', command: 'cd frontend && npm run build' },
    { id: 'lint', name: 'Linting', command: 'cd frontend && npm run lint' }
  ],
  'frontend': [
    { id: 'ui-components', name: 'UI Components', command: 'cd frontend && npm test -- --testPathPattern=components' },
    { id: 'pages', name: 'Pages', command: 'cd frontend && npm test -- --testPathPattern=pages' },
    { id: 'hooks', name: 'Hooks', command: 'cd frontend && npm test -- --testPathPattern=hooks' }
  ],
  'api': [
    { id: 'api-endpoints', name: 'API Endpoints', command: 'cd frontend && npm test -- --testPathPattern=api' },
    { id: 'supabase', name: 'Supabase Connection', command: 'node scripts/test-supabase-connection.js' },
    { id: 'google-cloud', name: 'Google Cloud Connection', command: 'node scripts/test-google-cloud-connection.js' }
  ],
  'integration': [
    { id: 'e2e', name: 'End-to-End Tests', command: 'cd frontend && npm test -- --testPathPattern=e2e' }
  ]
};

// Common issues and fixes
const commonIssues = {
  'Module not found': {
    pattern: /Module not found: Can't resolve '([^']+)'/,
    fix: (match) => {
      console.log(chalk.yellow(`Missing module: ${match[1]}`));
      console.log(chalk.green(`Installing missing module: ${match[1]}`));
      try {
        execSync(`cd frontend && npm install ${match[1]}`, { stdio: 'inherit' });
        return true;
      } catch (error) {
        console.error(chalk.red(`Failed to install module: ${match[1]}`));
        return false;
      }
    }
  },
  'Invalid import': {
    pattern: /Import .+ is invalid/,
    fix: () => {
      console.log(chalk.yellow('Invalid import detected'));
      return false;
    }
  },
  'Syntax error': {
    pattern: /SyntaxError: /,
    fix: () => {
      console.log(chalk.yellow('Syntax error detected'));
      return false;
    }
  },
  'Type error': {
    pattern: /TypeError: /,
    fix: () => {
      console.log(chalk.yellow('Type error detected'));
      return false;
    }
  }
};

// Run a test
function runTest(test) {
  console.log(chalk.blue(`Running test: ${test.name}`));
  try {
    execSync(test.command, { stdio: 'inherit' });
    console.log(chalk.green(`✓ Test passed: ${test.name}`));
    return { success: true };
  } catch (error) {
    console.log(chalk.red(`✗ Test failed: ${test.name}`));
    
    // Try to fix common issues
    const errorMessage = error.toString();
    let fixed = false;
    
    for (const [issueName, issue] of Object.entries(commonIssues)) {
      const match = errorMessage.match(issue.pattern);
      if (match) {
        console.log(chalk.yellow(`Detected issue: ${issueName}`));
        fixed = issue.fix(match);
        if (fixed) {
          console.log(chalk.green(`Fixed issue: ${issueName}`));
          
          // Try running the test again
          try {
            execSync(test.command, { stdio: 'inherit' });
            console.log(chalk.green(`✓ Test now passes: ${test.name}`));
            return { success: true, fixed: true };
          } catch (retryError) {
            console.log(chalk.red(`✗ Test still fails after fix: ${test.name}`));
          }
        }
      }
    }
    
    return { 
      success: false, 
      fixed: fixed,
      error: errorMessage
    };
  }
}

// Run tests for a category
function runCategoryTests(category) {
  console.log(chalk.blue(`\nRunning tests for category: ${category}`));
  
  const tests = testCategories[category];
  const results = {};
  
  for (const test of tests) {
    results[test.id] = runTest(test);
  }
  
  return results;
}

// Run all tests
function runAllTests() {
  console.log(chalk.blue('Running all tests'));
  
  const results = {};
  
  for (const category in testCategories) {
    const categoryResults = runCategoryTests(category);
    Object.assign(results, categoryResults);
  }
  
  return results;
}

// Generate a report
function generateReport(results) {
  console.log(chalk.blue('\nTest Report'));
  console.log(chalk.blue('==========='));
  
  let passed = 0;
  let failed = 0;
  let fixed = 0;
  
  for (const [testId, result] of Object.entries(results)) {
    if (result.success) {
      passed++;
      if (result.fixed) {
        fixed++;
      }
    } else {
      failed++;
    }
  }
  
  console.log(chalk.green(`Passed: ${passed}`));
  console.log(chalk.yellow(`Fixed: ${fixed}`));
  console.log(chalk.red(`Failed: ${failed}`));
  console.log(chalk.blue(`Total: ${passed + failed}`));
  
  if (failed > 0) {
    console.log(chalk.red('\nFailed Tests:'));
    for (const [testId, result] of Object.entries(results)) {
      if (!result.success) {
        // Find the test name
        let testName = testId;
        for (const category in testCategories) {
          const test = testCategories[category].find(t => t.id === testId);
          if (test) {
            testName = test.name;
            break;
          }
        }
        
        console.log(chalk.red(`- ${testName}`));
        console.log(chalk.gray(`  Error: ${result.error.split('\n')[0]}`));
      }
    }
  }
  
  return { passed, failed, fixed };
}

// Generate next steps
function generateNextSteps(report) {
  console.log(chalk.blue('\nNext Steps'));
  console.log(chalk.blue('=========='));
  
  if (report.failed > 0) {
    console.log(chalk.yellow('1. Fix the failing tests'));
    console.log(chalk.yellow('2. Run the tests again'));
  } else {
    console.log(chalk.green('All tests are passing! Here are some next steps:'));
    console.log(chalk.green('1. Deploy the application to Google Cloud Run'));
    console.log(chalk.green('2. Set up continuous integration with GitHub Actions'));
    console.log(chalk.green('3. Add more features to the application'));
    console.log(chalk.green('4. Add more tests for new features'));
  }
}

// Main function
function main() {
  console.log(chalk.blue('Comprehensive Test Script'));
  console.log(chalk.blue('=========================\n'));
  
  // Run all tests
  const results = runAllTests();
  
  // Generate a report
  const report = generateReport(results);
  
  // Generate next steps
  generateNextSteps(report);
}

// Run the main function
main();
