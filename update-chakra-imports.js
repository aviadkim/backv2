/**
 * Script to update Chakra UI imports in the project
 * 
 * This script updates the imports in the components to use our custom Chakra UI components
 */

const fs = require('fs');
const path = require('path');

// List of components to update
const componentsToUpdate = [
  'DevDocs/frontend/pages/FinancialAnalysisPage.js',
  'DevDocs/frontend/pages/ReportsPage.js',
  'DevDocs/frontend/pages/SettingsPage.js',
  'DevDocs/frontend/components/FinancialNotifications.js',
  'DevDocs/frontend/components/FinancialQueryEngine.js',
  'DevDocs/frontend/components/FinancialDocumentUploader.js'
];

// List of components that need to be imported from our custom components
const customComponents = [
  'TableContainer', 'Thead', 'Tbody', 'Tr', 'Th', 'Td',
  'TabList', 'Tab', 'TabPanels', 'TabPanel',
  'FormControl', 'FormLabel',
  'NumberInput', 'NumberInputField', 'NumberInputStepper',
  'NumberIncrementStepper', 'NumberDecrementStepper',
  'Divider', 'useToast'
];

// Update the imports in each component
componentsToUpdate.forEach(componentPath => {
  const fullPath = path.join(__dirname, componentPath);
  
  if (!fs.existsSync(fullPath)) {
    console.log(`Component not found: ${fullPath}`);
    return;
  }
  
  let content = fs.readFileSync(fullPath, 'utf8');
  
  // Check if the component imports any of the custom components
  const importsCustomComponents = customComponents.some(component => {
    return content.includes(`import { ${component}`) || 
           content.includes(`import {${component}`) || 
           content.includes(`, ${component}`) || 
           content.includes(`,${component}`);
  });
  
  if (!importsCustomComponents) {
    console.log(`No custom components imported in: ${componentPath}`);
    return;
  }
  
  // Add import for custom components
  const importStatement = "import { " + 
    customComponents.filter(component => 
      content.includes(`import { ${component}`) || 
      content.includes(`import {${component}`) || 
      content.includes(`, ${component}`) || 
      content.includes(`,${component}`)
    ).join(', ') + 
    " } from '../components/chakra-components';";
  
  // Remove the custom components from the @chakra-ui/react imports
  customComponents.forEach(component => {
    // Replace imports like "import { Component } from '@chakra-ui/react';"
    content = content.replace(new RegExp(`import\\s*{\\s*${component}\\s*}\\s*from\\s*['"]@chakra-ui/react['"]\\s*;`, 'g'), '');
    
    // Replace imports like "import { Component, OtherComponent } from '@chakra-ui/react';"
    content = content.replace(new RegExp(`(import\\s*{[^}]*),\\s*${component}\\s*([^}]*}\\s*from\\s*['"]@chakra-ui/react['"]\\s*;)`, 'g'), '$1$2');
    content = content.replace(new RegExp(`(import\\s*{[^}]*)\\s*${component},\\s*([^}]*}\\s*from\\s*['"]@chakra-ui/react['"]\\s*;)`, 'g'), '$1$2');
    
    // Clean up any empty imports
    content = content.replace(/import\s*{\s*}\s*from\s*['"]@chakra-ui\/react['"]\s*;/g, '');
  });
  
  // Add the import statement for custom components after the last import
  const lastImportIndex = content.lastIndexOf('import');
  const lastImportEndIndex = content.indexOf(';', lastImportIndex) + 1;
  
  content = content.slice(0, lastImportEndIndex) + '\n' + importStatement + content.slice(lastImportEndIndex);
  
  // Write the updated content back to the file
  fs.writeFileSync(fullPath, content, 'utf8');
  
  console.log(`Updated imports in: ${componentPath}`);
});

console.log('Chakra UI imports updated successfully!');
