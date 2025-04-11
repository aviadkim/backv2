/**
 * MCP Generator Script
 * 
 * This script generates Model, Controller, Provider, and Repository files
 * based on templates.
 * 
 * Usage:
 *   node mcp-generate.js model User "User model for authentication"
 *   node mcp-generate.js controller Document "Document management"
 *   node mcp-generate.js provider Portfolio "Portfolio data provider"
 *   node mcp-generate.js repository ISIN "ISIN data access"
 *   node mcp-generate.js all Document "Document management"
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Configuration
const config = require('../mcp.config.js');

// Command line arguments
const type = process.argv[2]?.toLowerCase();
const name = process.argv[3];
const description = process.argv[4] || '';

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Validate arguments
if (!type || !['model', 'controller', 'provider', 'repository', 'all'].includes(type)) {
  console.error('Error: Invalid type. Use model, controller, provider, repository, or all.');
  console.log('Usage: node mcp-generate.js <type> <name> [description]');
  process.exit(1);
}

if (!name) {
  console.error('Error: Name is required.');
  console.log('Usage: node mcp-generate.js <type> <name> [description]');
  process.exit(1);
}

// Ensure first letter is uppercase
const formattedName = name.charAt(0).toUpperCase() + name.slice(1);

// Function to generate a file based on template
function generateFile(templatePath, outputPath, replacements) {
  try {
    // Read template
    let template = fs.readFileSync(templatePath, 'utf8');
    
    // Replace placeholders
    Object.entries(replacements).forEach(([key, value]) => {
      const regex = new RegExp(`\\$\\{${key}\\}`, 'g');
      template = template.replace(regex, value);
    });
    
    // Create directory if it doesn't exist
    const dir = path.dirname(outputPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    // Write file
    fs.writeFileSync(outputPath, template);
    console.log(`Generated: ${outputPath}`);
    
    return true;
  } catch (error) {
    console.error(`Error generating file ${outputPath}:`, error);
    return false;
  }
}

// Function to generate a specific type
function generate(fileType) {
  const typeConfig = config.structure[fileType + 's'];
  if (!typeConfig) {
    console.error(`Error: Configuration for ${fileType} not found.`);
    return false;
  }
  
  const templatePath = typeConfig.template;
  const outputDir = typeConfig.dir;
  const extension = typeConfig.extension;
  
  // For repositories and controllers, use lowercase first letter in filename
  let filename;
  if (fileType === 'repository' || fileType === 'controller') {
    filename = `${formattedName.charAt(0).toLowerCase() + formattedName.slice(1)}${fileType.charAt(0).toUpperCase() + fileType.slice(1)}${extension}`;
  } else {
    filename = `${formattedName}${extension}`;
  }
  
  const outputPath = path.join(outputDir, filename);
  
  // Check if file already exists
  if (fs.existsSync(outputPath)) {
    return new Promise((resolve) => {
      rl.question(`File ${outputPath} already exists. Overwrite? (y/n): `, (answer) => {
        if (answer.toLowerCase() === 'y') {
          const success = generateFile(templatePath, outputPath, {
            name: formattedName,
            description: description
          });
          resolve(success);
        } else {
          console.log(`Skipped: ${outputPath}`);
          resolve(false);
        }
      });
    });
  } else {
    return Promise.resolve(generateFile(templatePath, outputPath, {
      name: formattedName,
      description: description
    }));
  }
}

// Main function
async function main() {
  try {
    if (type === 'all') {
      await generate('model');
      await generate('controller');
      await generate('provider');
      await generate('repository');
    } else {
      await generate(type);
    }
    
    console.log('Generation completed successfully.');
  } catch (error) {
    console.error('Error:', error);
  } finally {
    rl.close();
  }
}

// Run the main function
main();
