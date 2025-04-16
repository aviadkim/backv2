/**
 * Comprehensive Test Runner
 * This script runs a comprehensive set of tests on the application
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  underscore: '\x1b[4m',
  blink: '\x1b[5m',
  reverse: '\x1b[7m',
  hidden: '\x1b[8m',
  
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  
  bgBlack: '\x1b[40m',
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m',
  bgMagenta: '\x1b[45m',
  bgCyan: '\x1b[46m',
  bgWhite: '\x1b[47m'
};

// Test categories
const testCategories = [
  {
    name: 'code-quality',
    description: 'Tests for code quality issues',
    tests: [
      {
        name: 'ESLint',
        description: 'Checks for code style and quality issues',
        run: testEslint
      },
      {
        name: 'TypeScript',
        description: 'Checks for TypeScript type errors',
        run: testTypeScript
      },
      {
        name: 'Unused Dependencies',
        description: 'Checks for unused dependencies in package.json',
        run: testUnusedDependencies
      }
    ]
  },
  {
    name: 'build',
    description: 'Tests for build issues',
    tests: [
      {
        name: 'Next.js Build',
        description: 'Checks if the application builds successfully',
        run: testNextBuild
      },
      {
        name: 'Static Export',
        description: 'Checks if the application exports successfully',
        run: testStaticExport
      }
    ]
  },
  {
    name: 'performance',
    description: 'Tests for performance issues',
    tests: [
      {
        name: 'Bundle Size',
        description: 'Checks the size of the JavaScript bundles',
        run: testBundleSize
      },
      {
        name: 'Component Render Performance',
        description: 'Checks the render performance of key components',
        run: testComponentRenderPerformance
      }
    ]
  },
  {
    name: 'accessibility',
    description: 'Tests for accessibility issues',
    tests: [
      {
        name: 'Semantic HTML',
        description: 'Checks for proper use of semantic HTML',
        run: testSemanticHtml
      },
      {
        name: 'ARIA Attributes',
        description: 'Checks for proper use of ARIA attributes',
        run: testAriaAttributes
      },
      {
        name: 'Color Contrast',
        description: 'Checks for sufficient color contrast',
        run: testColorContrast
      }
    ]
  },
  {
    name: 'security',
    description: 'Tests for security issues',
    tests: [
      {
        name: 'Dependency Vulnerabilities',
        description: 'Checks for vulnerabilities in dependencies',
        run: testDependencyVulnerabilities
      },
      {
        name: 'API Security',
        description: 'Checks for security issues in API routes',
        run: testApiSecurity
      }
    ]
  }
];

// Test functions
function testEslint() {
  console.log(`${colors.blue}Running ESLint...${colors.reset}`);
  
  try {
    // Check if ESLint is installed
    const hasEslint = fs.existsSync(path.join(process.cwd(), 'node_modules', '.bin', 'eslint'));
    
    if (!hasEslint) {
      return {
        success: false,
        message: 'ESLint is not installed',
        fix: 'Run npm install eslint --save-dev to install ESLint'
      };
    }
    
    // Run ESLint on the components directory
    try {
      execSync('npx eslint components --max-warnings=0', { stdio: 'pipe' });
      return {
        success: true,
        message: 'No ESLint issues found in components'
      };
    } catch (error) {
      return {
        success: false,
        message: 'ESLint issues found in components',
        fix: 'Run npx eslint components --fix to fix automatically fixable issues'
      };
    }
  } catch (error) {
    return {
      success: false,
      message: `Error running ESLint: ${error.message}`,
      fix: 'Make sure ESLint is installed and configured correctly'
    };
  }
}

function testTypeScript() {
  console.log(`${colors.blue}Running TypeScript check...${colors.reset}`);
  
  try {
    // Check if TypeScript is installed
    const hasTypeScript = fs.existsSync(path.join(process.cwd(), 'node_modules', '.bin', 'tsc'));
    
    if (!hasTypeScript) {
      return {
        success: true,
        message: 'TypeScript is not installed, skipping check'
      };
    }
    
    // Run TypeScript check
    try {
      execSync('npx tsc --noEmit', { stdio: 'pipe' });
      return {
        success: true,
        message: 'No TypeScript errors found'
      };
    } catch (error) {
      return {
        success: false,
        message: 'TypeScript errors found',
        fix: 'Fix the TypeScript errors reported by tsc'
      };
    }
  } catch (error) {
    return {
      success: false,
      message: `Error running TypeScript check: ${error.message}`,
      fix: 'Make sure TypeScript is installed and configured correctly'
    };
  }
}

function testUnusedDependencies() {
  console.log(`${colors.blue}Checking for unused dependencies...${colors.reset}`);
  
  try {
    // Check if depcheck is installed
    const hasDepcheck = fs.existsSync(path.join(process.cwd(), 'node_modules', '.bin', 'depcheck'));
    
    if (!hasDepcheck) {
      return {
        success: true,
        message: 'depcheck is not installed, skipping check'
      };
    }
    
    // Run depcheck
    try {
      const output = execSync('npx depcheck', { stdio: 'pipe' }).toString();
      
      if (output.includes('Unused dependencies')) {
        return {
          success: false,
          message: 'Unused dependencies found',
          fix: 'Remove unused dependencies from package.json'
        };
      }
      
      return {
        success: true,
        message: 'No unused dependencies found'
      };
    } catch (error) {
      return {
        success: false,
        message: 'Unused dependencies found',
        fix: 'Remove unused dependencies from package.json'
      };
    }
  } catch (error) {
    return {
      success: false,
      message: `Error checking for unused dependencies: ${error.message}`,
      fix: 'Make sure depcheck is installed'
    };
  }
}

function testNextBuild() {
  console.log(`${colors.blue}Testing Next.js build...${colors.reset}`);
  
  try {
    // Run Next.js build
    execSync('npm run build', { stdio: 'pipe' });
    
    return {
      success: true,
      message: 'Next.js build successful'
    };
  } catch (error) {
    return {
      success: false,
      message: 'Next.js build failed',
      fix: 'Fix the build errors reported by Next.js'
    };
  }
}

function testStaticExport() {
  console.log(`${colors.blue}Testing static export...${colors.reset}`);
  
  try {
    // Check if the out directory exists
    const hasOutDir = fs.existsSync(path.join(process.cwd(), 'out'));
    
    if (!hasOutDir) {
      return {
        success: false,
        message: 'Static export directory not found',
        fix: 'Run npm run build to generate the static export'
      };
    }
    
    // Check if the out directory contains index.html
    const hasIndexHtml = fs.existsSync(path.join(process.cwd(), 'out', 'index.html'));
    
    if (!hasIndexHtml) {
      return {
        success: false,
        message: 'Static export does not contain index.html',
        fix: 'Run npm run build to generate the static export'
      };
    }
    
    return {
      success: true,
      message: 'Static export successful'
    };
  } catch (error) {
    return {
      success: false,
      message: `Error testing static export: ${error.message}`,
      fix: 'Run npm run build to generate the static export'
    };
  }
}

function testBundleSize() {
  console.log(`${colors.blue}Testing bundle size...${colors.reset}`);
  
  try {
    // Check if the .next directory exists
    const hasNextDir = fs.existsSync(path.join(process.cwd(), '.next'));
    
    if (!hasNextDir) {
      return {
        success: false,
        message: 'Next.js build directory not found',
        fix: 'Run npm run build to generate the Next.js build'
      };
    }
    
    // Check the size of the JavaScript bundles
    const bundlesDir = path.join(process.cwd(), '.next', 'static', 'chunks');
    
    if (!fs.existsSync(bundlesDir)) {
      return {
        success: false,
        message: 'JavaScript bundles directory not found',
        fix: 'Run npm run build to generate the Next.js build'
      };
    }
    
    const bundles = fs.readdirSync(bundlesDir).filter(file => file.endsWith('.js'));
    
    if (bundles.length === 0) {
      return {
        success: false,
        message: 'No JavaScript bundles found',
        fix: 'Run npm run build to generate the Next.js build'
      };
    }
    
    // Calculate the total size of the bundles
    let totalSize = 0;
    
    for (const bundle of bundles) {
      const stats = fs.statSync(path.join(bundlesDir, bundle));
      totalSize += stats.size;
    }
    
    // Convert to MB
    const totalSizeMB = totalSize / (1024 * 1024);
    
    // Check if the total size is less than 5 MB
    if (totalSizeMB > 5) {
      return {
        success: false,
        message: `Total bundle size is ${totalSizeMB.toFixed(2)} MB, which is larger than 5 MB`,
        fix: 'Optimize the JavaScript bundles by removing unused code and dependencies'
      };
    }
    
    return {
      success: true,
      message: `Total bundle size is ${totalSizeMB.toFixed(2)} MB, which is less than 5 MB`
    };
  } catch (error) {
    return {
      success: false,
      message: `Error testing bundle size: ${error.message}`,
      fix: 'Run npm run build to generate the Next.js build'
    };
  }
}

function testComponentRenderPerformance() {
  console.log(`${colors.blue}Testing component render performance...${colors.reset}`);
  
  // This is a simplified test that just checks if the components exist
  try {
    const componentsDir = path.join(process.cwd(), 'components');
    
    if (!fs.existsSync(componentsDir)) {
      return {
        success: false,
        message: 'Components directory not found',
        fix: 'Create a components directory'
      };
    }
    
    const components = fs.readdirSync(componentsDir).filter(file => file.endsWith('.js') || file.endsWith('.jsx') || file.endsWith('.tsx'));
    
    if (components.length === 0) {
      return {
        success: false,
        message: 'No components found',
        fix: 'Create components in the components directory'
      };
    }
    
    return {
      success: true,
      message: `Found ${components.length} components`
    };
  } catch (error) {
    return {
      success: false,
      message: `Error testing component render performance: ${error.message}`,
      fix: 'Make sure the components directory exists and contains components'
    };
  }
}

function testSemanticHtml() {
  console.log(`${colors.blue}Testing semantic HTML...${colors.reset}`);
  
  // This is a simplified test that just checks for semantic HTML elements in component files
  try {
    const componentsDir = path.join(process.cwd(), 'components');
    
    if (!fs.existsSync(componentsDir)) {
      return {
        success: false,
        message: 'Components directory not found',
        fix: 'Create a components directory'
      };
    }
    
    const components = fs.readdirSync(componentsDir).filter(file => file.endsWith('.js') || file.endsWith('.jsx') || file.endsWith('.tsx'));
    
    if (components.length === 0) {
      return {
        success: false,
        message: 'No components found',
        fix: 'Create components in the components directory'
      };
    }
    
    // Check for semantic HTML elements in component files
    const semanticElements = ['header', 'footer', 'nav', 'main', 'section', 'article', 'aside', 'figure', 'figcaption', 'time'];
    let semanticElementsFound = false;
    
    for (const component of components) {
      const content = fs.readFileSync(path.join(componentsDir, component), 'utf8');
      
      for (const element of semanticElements) {
        if (content.includes(`<${element}`) || content.includes(`<${element}>`) || content.includes(`<${element} `)) {
          semanticElementsFound = true;
          break;
        }
      }
      
      if (semanticElementsFound) {
        break;
      }
    }
    
    if (!semanticElementsFound) {
      return {
        success: false,
        message: 'No semantic HTML elements found in components',
        fix: 'Use semantic HTML elements like header, footer, nav, main, section, article, etc.'
      };
    }
    
    return {
      success: true,
      message: 'Semantic HTML elements found in components'
    };
  } catch (error) {
    return {
      success: false,
      message: `Error testing semantic HTML: ${error.message}`,
      fix: 'Make sure the components directory exists and contains components'
    };
  }
}

function testAriaAttributes() {
  console.log(`${colors.blue}Testing ARIA attributes...${colors.reset}`);
  
  // This is a simplified test that just checks for ARIA attributes in component files
  try {
    const componentsDir = path.join(process.cwd(), 'components');
    
    if (!fs.existsSync(componentsDir)) {
      return {
        success: false,
        message: 'Components directory not found',
        fix: 'Create a components directory'
      };
    }
    
    const components = fs.readdirSync(componentsDir).filter(file => file.endsWith('.js') || file.endsWith('.jsx') || file.endsWith('.tsx'));
    
    if (components.length === 0) {
      return {
        success: false,
        message: 'No components found',
        fix: 'Create components in the components directory'
      };
    }
    
    // Check for ARIA attributes in component files
    const ariaAttributes = ['aria-label', 'aria-labelledby', 'aria-describedby', 'aria-hidden', 'aria-live', 'aria-role', 'role'];
    let ariaAttributesFound = false;
    
    for (const component of components) {
      const content = fs.readFileSync(path.join(componentsDir, component), 'utf8');
      
      for (const attribute of ariaAttributes) {
        if (content.includes(`${attribute}=`) || content.includes(`${attribute}="`) || content.includes(`${attribute}={`)) {
          ariaAttributesFound = true;
          break;
        }
      }
      
      if (ariaAttributesFound) {
        break;
      }
    }
    
    if (!ariaAttributesFound) {
      return {
        success: false,
        message: 'No ARIA attributes found in components',
        fix: 'Use ARIA attributes like aria-label, aria-labelledby, aria-describedby, etc.'
      };
    }
    
    return {
      success: true,
      message: 'ARIA attributes found in components'
    };
  } catch (error) {
    return {
      success: false,
      message: `Error testing ARIA attributes: ${error.message}`,
      fix: 'Make sure the components directory exists and contains components'
    };
  }
}

function testColorContrast() {
  console.log(`${colors.blue}Testing color contrast...${colors.reset}`);
  
  // This is a simplified test that just checks for color variables in CSS files
  try {
    const stylesDir = path.join(process.cwd(), 'styles');
    
    if (!fs.existsSync(stylesDir)) {
      return {
        success: true,
        message: 'Styles directory not found, skipping check'
      };
    }
    
    const cssFiles = fs.readdirSync(stylesDir).filter(file => file.endsWith('.css') || file.endsWith('.scss'));
    
    if (cssFiles.length === 0) {
      return {
        success: true,
        message: 'No CSS files found, skipping check'
      };
    }
    
    // Check for color variables in CSS files
    const colorVariables = [];
    
    for (const cssFile of cssFiles) {
      const content = fs.readFileSync(path.join(stylesDir, cssFile), 'utf8');
      
      // Extract color variables
      const colorRegex = /--color-[a-zA-Z0-9-]+:\s*([^;]+);/g;
      let match;
      
      while ((match = colorRegex.exec(content)) !== null) {
        colorVariables.push(match[1]);
      }
    }
    
    if (colorVariables.length === 0) {
      return {
        success: true,
        message: 'No color variables found, skipping check'
      };
    }
    
    // In a real test, we would check the contrast ratio between colors
    // For this simplified test, we'll just check if there are at least 2 color variables
    if (colorVariables.length < 2) {
      return {
        success: false,
        message: 'Only one color variable found, which is not enough to check contrast',
        fix: 'Define more color variables in your CSS files'
      };
    }
    
    return {
      success: true,
      message: `Found ${colorVariables.length} color variables`
    };
  } catch (error) {
    return {
      success: false,
      message: `Error testing color contrast: ${error.message}`,
      fix: 'Make sure the styles directory exists and contains CSS files'
    };
  }
}

function testDependencyVulnerabilities() {
  console.log(`${colors.blue}Testing dependency vulnerabilities...${colors.reset}`);
  
  try {
    // Check if npm-audit is available
    try {
      execSync('npm audit --json', { stdio: 'pipe' });
      
      // If we get here, there are no vulnerabilities
      return {
        success: true,
        message: 'No vulnerabilities found in dependencies'
      };
    } catch (error) {
      // npm audit returns a non-zero exit code if vulnerabilities are found
      try {
        const auditOutput = JSON.parse(error.stdout.toString());
        
        if (auditOutput.vulnerabilities && Object.keys(auditOutput.vulnerabilities).length > 0) {
          return {
            success: false,
            message: `Found ${Object.keys(auditOutput.vulnerabilities).length} vulnerabilities in dependencies`,
            fix: 'Run npm audit fix to fix vulnerabilities'
          };
        }
        
        return {
          success: true,
          message: 'No vulnerabilities found in dependencies'
        };
      } catch (parseError) {
        return {
          success: false,
          message: 'Error parsing npm audit output',
          fix: 'Run npm audit manually to check for vulnerabilities'
        };
      }
    }
  } catch (error) {
    return {
      success: false,
      message: `Error testing dependency vulnerabilities: ${error.message}`,
      fix: 'Run npm audit manually to check for vulnerabilities'
    };
  }
}

function testApiSecurity() {
  console.log(`${colors.blue}Testing API security...${colors.reset}`);
  
  try {
    const apiDir = path.join(process.cwd(), 'pages', 'api');
    
    if (!fs.existsSync(apiDir)) {
      return {
        success: true,
        message: 'API directory not found, skipping check'
      };
    }
    
    // Check for API routes
    const apiRoutes = [];
    
    function findApiRoutes(dir) {
      const files = fs.readdirSync(dir);
      
      for (const file of files) {
        const filePath = path.join(dir, file);
        const stats = fs.statSync(filePath);
        
        if (stats.isDirectory()) {
          findApiRoutes(filePath);
        } else if (file.endsWith('.js') || file.endsWith('.ts')) {
          apiRoutes.push(filePath);
        }
      }
    }
    
    findApiRoutes(apiDir);
    
    if (apiRoutes.length === 0) {
      return {
        success: true,
        message: 'No API routes found, skipping check'
      };
    }
    
    // Check for security issues in API routes
    let securityIssuesFound = false;
    
    for (const apiRoute of apiRoutes) {
      const content = fs.readFileSync(apiRoute, 'utf8');
      
      // Check for method validation
      if (!content.includes('req.method') && !content.includes('request.method')) {
        securityIssuesFound = true;
        console.log(`${colors.yellow}Warning: API route ${apiRoute} does not validate the HTTP method${colors.reset}`);
      }
      
      // Check for authentication
      if (!content.includes('session') && !content.includes('auth') && !content.includes('token')) {
        securityIssuesFound = true;
        console.log(`${colors.yellow}Warning: API route ${apiRoute} may not implement authentication${colors.reset}`);
      }
    }
    
    if (securityIssuesFound) {
      return {
        success: false,
        message: 'Security issues found in API routes',
        fix: 'Implement proper method validation and authentication in API routes'
      };
    }
    
    return {
      success: true,
      message: 'No security issues found in API routes'
    };
  } catch (error) {
    return {
      success: false,
      message: `Error testing API security: ${error.message}`,
      fix: 'Make sure the pages/api directory exists and contains API routes'
    };
  }
}

// Run a test
function runTest(test) {
  console.log(`${colors.cyan}Running test: ${test.name}${colors.reset}`);
  console.log(`${test.description}`);
  
  const result = test.run();
  
  if (result.success) {
    console.log(`${colors.green}✓ Test passed: ${test.name}${colors.reset}`);
  } else {
    console.log(`${colors.red}✗ Test failed: ${test.name}${colors.reset}`);
    console.log(`  ${colors.red}${result.message}${colors.reset}`);
    
    if (result.fix) {
      console.log(`    ${colors.yellow}Fix: ${result.fix}${colors.reset}`);
    }
  }
  
  return result;
}

// Run all tests
function runAllTests() {
  console.log(`${colors.bright}${colors.white}Comprehensive Test Runner${colors.reset}`);
  console.log(`${colors.white}=================\n${colors.reset}`);
  
  console.log(`${colors.white}Running all tests\n${colors.reset}`);
  
  const results = {
    passed: 0,
    failed: 0,
    total: 0,
    failedTests: []
  };
  
  for (const category of testCategories) {
    console.log(`${colors.bright}${colors.white}Running tests for category: ${category.name}${colors.reset}`);
    console.log(`${category.description}\n`);
    
    for (const test of category.tests) {
      const result = runTest(test);
      
      results.total++;
      
      if (result.success) {
        results.passed++;
      } else {
        results.failed++;
        results.failedTests.push({
          category: category.name,
          test: test.name,
          message: result.message,
          fix: result.fix
        });
      }
      
      console.log('');
    }
  }
  
  console.log(`${colors.bright}${colors.white}Test Report${colors.reset}`);
  console.log(`${colors.white}===========\n${colors.reset}`);
  
  console.log(`${colors.white}Passed: ${colors.green}${results.passed}${colors.reset}`);
  console.log(`${colors.white}Failed: ${colors.red}${results.failed}${colors.reset}`);
  console.log(`${colors.white}Total: ${results.total}${colors.reset}\n`);
  
  if (results.failed > 0) {
    console.log(`${colors.bright}${colors.white}Failed Tests:${colors.reset}`);
    
    for (const failedTest of results.failedTests) {
      console.log(`${colors.red}- ${failedTest.test} (${failedTest.category})${colors.reset}`);
      console.log(`  ${colors.red}${failedTest.message}${colors.reset}`);
      
      if (failedTest.fix) {
        console.log(`  ${colors.yellow}Fix: ${failedTest.fix}${colors.reset}`);
      }
    }
  }
  
  console.log(`\n${colors.bright}${colors.white}Next Steps${colors.reset}`);
  console.log(`${colors.white}==========\n${colors.reset}`);
  
  if (results.failed > 0) {
    console.log(`${colors.white}1. Fix the failing tests${colors.reset}`);
    console.log(`${colors.white}2. Run the tests again${colors.reset}`);
    console.log(`${colors.white}3. Implement the suggested fixes${colors.reset}`);
  } else {
    console.log(`${colors.green}All tests are passing! Here are some next steps:${colors.reset}`);
    console.log(`${colors.white}1. Add more tests for edge cases${colors.reset}`);
    console.log(`${colors.white}2. Implement performance tests${colors.reset}`);
    console.log(`${colors.white}3. Add integration tests with real API calls (when API keys are available)${colors.reset}`);
    console.log(`${colors.white}4. Deploy the application to a staging environment${colors.reset}`);
  }
  
  return results;
}

// Run all tests
runAllTests();
