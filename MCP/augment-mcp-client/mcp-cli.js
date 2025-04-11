#!/usr/bin/env node

/**
 * MCP CLI Tool
 * 
 * Command-line interface for the MCP Client.
 */

const MCPClient = require('./mcp-client');
const { program } = require('commander');
const inquirer = require('inquirer');
const chalk = require('chalk');

const client = new MCPClient();

// Check if server is running
async function checkServer() {
  const isRunning = await client.isServerRunning();
  if (!isRunning) {
    console.error(chalk.red('Error: MCP Server is not running.'));
    console.log(chalk.yellow('Start the server with:'));
    console.log(chalk.cyan('  .\\start-mcp-server.ps1'));
    process.exit(1);
  }
}

// Generate component command
program
  .command('generate')
  .description('Generate a new component')
  .option('-p, --project <projectId>', 'Project ID')
  .option('-t, --type <type>', 'Component type (model, controller, provider, repository)')
  .option('-n, --name <name>', 'Component name')
  .option('-d, --description <description>', 'Component description')
  .action(async (options) => {
    await checkServer();
    
    try {
      // If options are missing, prompt for them
      const answers = await promptMissingOptions(options);
      
      // Combine options and answers
      const { project, type, name, description } = { ...options, ...answers };
      
      console.log(chalk.cyan(`Generating ${type} component: ${name}...`));
      
      const result = await client.generateComponent(project, type, name, description);
      
      console.log(chalk.green('Component generated successfully!'));
      console.log(chalk.yellow('Path:'), result.path);
    } catch (error) {
      console.error(chalk.red('Error generating component:'), error.message);
    }
  });

// List projects command
program
  .command('list-projects')
  .description('List available projects')
  .action(async () => {
    await checkServer();
    
    try {
      const projects = await client.getProjects();
      
      console.log(chalk.green('Available projects:'));
      projects.forEach(project => {
        console.log(chalk.cyan(`- ${project}`));
      });
    } catch (error) {
      console.error(chalk.red('Error listing projects:'), error.message);
    }
  });

// Add project command
program
  .command('add-project')
  .description('Add a new project')
  .option('-i, --id <projectId>', 'Project ID')
  .option('-r, --root <rootPath>', 'Project root path')
  .action(async (options) => {
    await checkServer();
    
    try {
      // If options are missing, prompt for them
      const answers = await promptMissingProjectOptions(options);
      
      // Combine options and answers
      const { id, root } = { ...options, ...answers };
      
      // Default structure
      const structure = {
        models: 'models',
        controllers: 'controllers',
        providers: 'providers',
        repositories: 'repositories'
      };
      
      console.log(chalk.cyan(`Adding project: ${id}...`));
      
      const result = await client.addProject(id, root, structure);
      
      console.log(chalk.green('Project added successfully!'));
      console.log(chalk.yellow('Root path:'), result.rootPath);
    } catch (error) {
      console.error(chalk.red('Error adding project:'), error.message);
    }
  });

// Generate all components command
program
  .command('generate-all')
  .description('Generate all components for a feature')
  .option('-p, --project <projectId>', 'Project ID')
  .option('-n, --name <name>', 'Component name')
  .option('-d, --description <description>', 'Component description')
  .action(async (options) => {
    await checkServer();
    
    try {
      // If options are missing, prompt for them
      const answers = await promptMissingAllOptions(options);
      
      // Combine options and answers
      const { project, name, description } = { ...options, ...answers };
      
      console.log(chalk.cyan(`Generating all components for: ${name}...`));
      
      // Generate model
      await client.generateComponent(project, 'model', name, description);
      console.log(chalk.green('Model generated successfully!'));
      
      // Generate repository
      await client.generateComponent(project, 'repository', name, description);
      console.log(chalk.green('Repository generated successfully!'));
      
      // Generate controller
      await client.generateComponent(project, 'controller', name, description);
      console.log(chalk.green('Controller generated successfully!'));
      
      // Generate provider
      await client.generateComponent(project, 'provider', name, description);
      console.log(chalk.green('Provider generated successfully!'));
      
      console.log(chalk.green('All components generated successfully!'));
    } catch (error) {
      console.error(chalk.red('Error generating components:'), error.message);
    }
  });

// Helper function to prompt for missing options
async function promptMissingOptions(options) {
  const questions = [];
  
  if (!options.project) {
    // Get available projects
    const projects = await client.getProjects();
    
    questions.push({
      type: 'list',
      name: 'project',
      message: 'Select a project:',
      choices: projects
    });
  }
  
  if (!options.type) {
    questions.push({
      type: 'list',
      name: 'type',
      message: 'Select component type:',
      choices: ['model', 'controller', 'provider', 'repository']
    });
  }
  
  if (!options.name) {
    questions.push({
      type: 'input',
      name: 'name',
      message: 'Enter component name:',
      validate: input => input.trim() !== '' ? true : 'Name is required'
    });
  }
  
  if (!options.description) {
    questions.push({
      type: 'input',
      name: 'description',
      message: 'Enter component description:',
      default: ''
    });
  }
  
  return inquirer.prompt(questions);
}

// Helper function to prompt for missing project options
async function promptMissingProjectOptions(options) {
  const questions = [];
  
  if (!options.id) {
    questions.push({
      type: 'input',
      name: 'id',
      message: 'Enter project ID:',
      validate: input => input.trim() !== '' ? true : 'Project ID is required'
    });
  }
  
  if (!options.root) {
    questions.push({
      type: 'input',
      name: 'root',
      message: 'Enter project root path:',
      validate: input => input.trim() !== '' ? true : 'Root path is required'
    });
  }
  
  return inquirer.prompt(questions);
}

// Helper function to prompt for missing all options
async function promptMissingAllOptions(options) {
  const questions = [];
  
  if (!options.project) {
    // Get available projects
    const projects = await client.getProjects();
    
    questions.push({
      type: 'list',
      name: 'project',
      message: 'Select a project:',
      choices: projects
    });
  }
  
  if (!options.name) {
    questions.push({
      type: 'input',
      name: 'name',
      message: 'Enter component name:',
      validate: input => input.trim() !== '' ? true : 'Name is required'
    });
  }
  
  if (!options.description) {
    questions.push({
      type: 'input',
      name: 'description',
      message: 'Enter component description:',
      default: ''
    });
  }
  
  return inquirer.prompt(questions);
}

// Parse command line arguments
program.parse(process.argv);
