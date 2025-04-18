#!/usr/bin/env node

/**
 * Setup Project Structure Script
 * 
 * This script creates the necessary directory structure for the FinDoc Analyzer project
 * with clear separation of concerns.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Define the project structure
const projectStructure = {
  'DevDocs': {
    'backend': {
      'agents': {},
      'controllers': {},
      'db': {},
      'middleware': {},
      'models': {},
      'routes': {
        'api': {
          'auth': {},
          'financial': {},
          'integration': {},
          'performance': {},
          'security': {}
        }
      },
      'services': {
        'agents': {},
        'auth': {},
        'cache': {},
        'document-processing': {},
        'performance': {},
        'security': {}
      },
      'tests': {
        'samples': {}
      },
      'utils': {}
    },
    'frontend': {
      'components': {},
      'contexts': {},
      'hooks': {},
      'lib': {},
      'pages': {
        'api': {
          'auth': {},
          'financial': {}
        }
      },
      'providers': {},
      'public': {
        'images': {}
      },
      'styles': {},
      'utils': {}
    },
    'docs': {
      'api': {},
      'deployment': {},
      'development': {},
      'user-guides': {}
    }
  }
};

// Create directories recursively
function createDirectories(structure, basePath = '') {
  for (const [name, subDirs] of Object.entries(structure)) {
    const dirPath = path.join(basePath, name);
    
    // Create directory if it doesn't exist
    if (!fs.existsSync(dirPath)) {
      console.log(`Creating directory: ${dirPath}`);
      fs.mkdirSync(dirPath, { recursive: true });
    }
    
    // Create subdirectories
    if (Object.keys(subDirs).length > 0) {
      createDirectories(subDirs, dirPath);
    }
  }
}

// Create README files for each directory
function createReadmeFiles(structure, basePath = '') {
  for (const [name, subDirs] of Object.entries(structure)) {
    const dirPath = path.join(basePath, name);
    const readmePath = path.join(dirPath, 'README.md');
    
    // Create README file if it doesn't exist
    if (!fs.existsSync(readmePath)) {
      console.log(`Creating README: ${readmePath}`);
      
      const readmeContent = `# ${name}\n\n` +
        `This directory contains the ${name.toLowerCase()} components of the FinDoc Analyzer project.\n\n` +
        `## Purpose\n\n` +
        `Describe the purpose of this directory and its contents.\n\n` +
        `## Structure\n\n` +
        `- List the key files and subdirectories here\n`;
      
      fs.writeFileSync(readmePath, readmeContent);
    }
    
    // Create README files for subdirectories
    if (Object.keys(subDirs).length > 0) {
      createReadmeFiles(subDirs, dirPath);
    }
  }
}

// Create .gitkeep files for empty directories
function createGitkeepFiles(structure, basePath = '') {
  for (const [name, subDirs] of Object.entries(structure)) {
    const dirPath = path.join(basePath, name);
    
    // Check if directory is empty (no files other than README.md)
    const files = fs.readdirSync(dirPath);
    const nonReadmeFiles = files.filter(file => file !== 'README.md');
    
    if (nonReadmeFiles.length === 0) {
      const gitkeepPath = path.join(dirPath, '.gitkeep');
      
      if (!fs.existsSync(gitkeepPath)) {
        console.log(`Creating .gitkeep: ${gitkeepPath}`);
        fs.writeFileSync(gitkeepPath, '');
      }
    }
    
    // Create .gitkeep files for subdirectories
    if (Object.keys(subDirs).length > 0) {
      createGitkeepFiles(subDirs, dirPath);
    }
  }
}

// Main function
function main() {
  console.log('Setting up project structure for FinDoc Analyzer...');
  
  // Create directories
  createDirectories(projectStructure);
  
  // Create README files
  createReadmeFiles(projectStructure);
  
  // Create .gitkeep files
  createGitkeepFiles(projectStructure);
  
  console.log('Project structure setup complete!');
}

// Run the script
main();
