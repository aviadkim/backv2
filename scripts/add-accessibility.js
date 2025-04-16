/**
 * Script to add accessibility features to components
 */

const fs = require('fs');
const path = require('path');

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

console.log(`${colors.bright}${colors.white}Accessibility Enhancer${colors.reset}`);
console.log(`${colors.white}=====================\n${colors.reset}`);

// Get the components directory
const componentsDir = path.join(process.cwd(), 'components');

if (!fs.existsSync(componentsDir)) {
  console.log(`${colors.red}Components directory not found: ${componentsDir}${colors.reset}`);
  process.exit(1);
}

// Get all component files
const componentFiles = fs.readdirSync(componentsDir).filter(file => 
  file.endsWith('.js') || file.endsWith('.jsx') || file.endsWith('.tsx')
);

if (componentFiles.length === 0) {
  console.log(`${colors.red}No component files found in ${componentsDir}${colors.reset}`);
  process.exit(1);
}

console.log(`${colors.green}Found ${componentFiles.length} component files${colors.reset}`);

// Process each component file
let modifiedFiles = 0;

for (const file of componentFiles) {
  const filePath = path.join(componentsDir, file);
  console.log(`${colors.blue}Processing ${file}...${colors.reset}`);
  
  // Read the file
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;
  
  // Check if the component already has accessibility features
  const hasAriaAttributes = content.includes('aria-') || content.includes('role=');
  const hasSemanticElements = content.includes('<header') || content.includes('<footer') || 
                             content.includes('<nav') || content.includes('<main') || 
                             content.includes('<section') || content.includes('<article');
  
  if (hasAriaAttributes && hasSemanticElements) {
    console.log(`${colors.green}Component already has accessibility features${colors.reset}`);
    continue;
  }
  
  // Add import for AccessibilityWrapper if needed
  if (!content.includes('import AccessibilityWrapper')) {
    const importRegex = /import\s+React(?:,\s*\{[^}]*\})?\s+from\s+['"]react['"];?/;
    const importMatch = content.match(importRegex);
    
    if (importMatch) {
      const newImport = `${importMatch[0]}\nimport AccessibilityWrapper from './AccessibilityWrapper';`;
      content = content.replace(importMatch[0], newImport);
      modified = true;
    } else {
      const newImport = `import React from 'react';\nimport AccessibilityWrapper from './AccessibilityWrapper';`;
      content = newImport + '\n\n' + content;
      modified = true;
    }
  }
  
  // Add semantic elements
  if (!hasSemanticElements) {
    // Replace div with className="header" with header
    content = content.replace(/<div([^>]*className=['"][^'"]*header[^'"]*['"][^>]*)>/g, '<header$1>');
    content = content.replace(/<\/div>([^<]*<div[^>]*className=['"][^'"]*header-content[^'"]*['"][^>]*>)/g, '</header>$1');
    
    // Replace div with className="footer" with footer
    content = content.replace(/<div([^>]*className=['"][^'"]*footer[^'"]*['"][^>]*)>/g, '<footer$1>');
    content = content.replace(/<\/div>([^<]*<div[^>]*className=['"][^'"]*footer-content[^'"]*['"][^>]*>)/g, '</footer>$1');
    
    // Replace div with className="nav" with nav
    content = content.replace(/<div([^>]*className=['"][^'"]*nav[^'"]*['"][^>]*)>/g, '<nav$1>');
    content = content.replace(/<\/div>([^<]*<div[^>]*className=['"][^'"]*nav-content[^'"]*['"][^>]*>)/g, '</nav>$1');
    
    // Replace div with className="main" with main
    content = content.replace(/<div([^>]*className=['"][^'"]*main[^'"]*['"][^>]*)>/g, '<main$1>');
    content = content.replace(/<\/div>([^<]*<div[^>]*className=['"][^'"]*main-content[^'"]*['"][^>]*>)/g, '</main>$1');
    
    // Replace div with className="section" with section
    content = content.replace(/<div([^>]*className=['"][^'"]*section[^'"]*['"][^>]*)>/g, '<section$1>');
    content = content.replace(/<\/div>([^<]*<div[^>]*className=['"][^'"]*section-content[^'"]*['"][^>]*>)/g, '</section>$1');
    
    modified = true;
  }
  
  // Add ARIA attributes
  if (!hasAriaAttributes) {
    // Add role to div elements
    content = content.replace(/<div([^>]*)>/g, (match, attributes) => {
      if (attributes.includes('role=')) {
        return match;
      }
      
      if (attributes.includes('className=')) {
        if (attributes.includes('className="container"')) {
          return `<div${attributes} role="main">`;
        } else if (attributes.includes('className="header"')) {
          return `<div${attributes} role="banner">`;
        } else if (attributes.includes('className="footer"')) {
          return `<div${attributes} role="contentinfo">`;
        } else if (attributes.includes('className="nav"')) {
          return `<div${attributes} role="navigation">`;
        } else if (attributes.includes('className="sidebar"')) {
          return `<div${attributes} role="complementary">`;
        } else if (attributes.includes('className="content"')) {
          return `<div${attributes} role="main">`;
        } else {
          return match;
        }
      }
      
      return match;
    });
    
    // Add aria-label to buttons
    content = content.replace(/<button([^>]*)>/g, (match, attributes) => {
      if (attributes.includes('aria-label=')) {
        return match;
      }
      
      if (attributes.includes('className=')) {
        if (attributes.includes('className="close"')) {
          return `<button${attributes} aria-label="Close">`;
        } else if (attributes.includes('className="menu"')) {
          return `<button${attributes} aria-label="Menu">`;
        } else if (attributes.includes('className="search"')) {
          return `<button${attributes} aria-label="Search">`;
        } else {
          return match;
        }
      }
      
      return match;
    });
    
    modified = true;
  }
  
  // Wrap the component with AccessibilityWrapper
  if (modified) {
    // Find the return statement
    const returnRegex = /return\s*\(/;
    const returnMatch = content.match(returnRegex);
    
    if (returnMatch) {
      const returnIndex = returnMatch.index + returnMatch[0].length;
      const beforeReturn = content.substring(0, returnIndex);
      const afterReturn = content.substring(returnIndex);
      
      // Add AccessibilityWrapper
      content = beforeReturn + '\n    <AccessibilityWrapper>\n      ' + 
                afterReturn.replace(/\);(\s*)$/, '\n    </AccessibilityWrapper>\n  );$1');
    }
  }
  
  // Save the file if modified
  if (modified) {
    fs.writeFileSync(filePath, content);
    console.log(`${colors.green}Added accessibility features to ${file}${colors.reset}`);
    modifiedFiles++;
  } else {
    console.log(`${colors.yellow}No changes needed for ${file}${colors.reset}`);
  }
}

console.log(`\n${colors.green}Added accessibility features to ${modifiedFiles} component files${colors.reset}`);
