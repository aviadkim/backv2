/**
 * Augment MCP Server
 *
 * This server provides a global MCP (Model, Controller, Provider) architecture
 * for Augment projects.
 */

const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const winston = require('winston');

// Load configuration
const config = require('./config.json');

// Configure logger
const logger = winston.createLogger({
  level: config.logging.level,
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: config.logging.file })
  ]
});

// Initialize Express app
const app = express();
app.use(cors());
app.use(bodyParser.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', version: config.version });
});

// Get available projects
app.get('/projects', (req, res) => {
  res.json({ projects: Object.keys(config.projects) });
});

// Get project structure
app.get('/projects/:projectId', (req, res) => {
  const { projectId } = req.params;

  if (!config.projects[projectId]) {
    return res.status(404).json({ error: `Project ${projectId} not found` });
  }

  res.json({ project: config.projects[projectId] });
});

// Generate component
app.post('/generate', (req, res) => {
  const { projectId, type, name, description } = req.body;

  if (!projectId || !type || !name) {
    return res.status(400).json({ error: 'Missing required parameters: projectId, type, name' });
  }

  if (!config.projects[projectId]) {
    return res.status(404).json({ error: `Project ${projectId} not found` });
  }

  if (!['model', 'controller', 'provider', 'repository'].includes(type)) {
    return res.status(400).json({ error: `Invalid type: ${type}. Must be one of: model, controller, provider, repository` });
  }

  try {
    const result = generateComponent(projectId, type, name, description || '');
    res.json({ success: true, result });
  } catch (error) {
    logger.error('Error generating component', { error: error.message, projectId, type, name });
    res.status(500).json({ error: error.message });
  }
});

// Add project
app.post('/projects', (req, res) => {
  const { projectId, rootPath, structure } = req.body;

  if (!projectId || !rootPath || !structure) {
    return res.status(400).json({ error: 'Missing required parameters: projectId, rootPath, structure' });
  }

  if (config.projects[projectId]) {
    return res.status(409).json({ error: `Project ${projectId} already exists` });
  }

  try {
    // Add project to config
    config.projects[projectId] = {
      rootPath,
      structure
    };

    // Save updated config
    fs.writeFileSync(
      path.join(__dirname, 'config.json'),
      JSON.stringify(config, null, 2)
    );

    res.json({ success: true, project: config.projects[projectId] });
  } catch (error) {
    logger.error('Error adding project', { error: error.message, projectId });
    res.status(500).json({ error: error.message });
  }
});

// Function to generate a component
function generateComponent(projectId, type, name, description) {
  const project = config.projects[projectId];
  const templatePath = path.join(__dirname, config.templates.basePath, `${type}.template${config.templates.extensions[type]}`);

  // Ensure template exists
  if (!fs.existsSync(templatePath)) {
    throw new Error(`Template not found: ${templatePath}`);
  }

  // Read template
  const template = fs.readFileSync(templatePath, 'utf8');

  // Format name (ensure first letter is uppercase)
  const formattedName = name.charAt(0).toUpperCase() + name.slice(1);

  try {
    // Replace placeholders
    let content = template
      .replace(/\${name}/g, formattedName)
      .replace(/\${description}/g, description);

    // Special handling for repository and controller templates
    if (type === 'repository' || type === 'controller') {
      // Replace lowercase name references
      content = content.replace(/\${name\.toLowerCase\(\)}/g, formattedName.charAt(0).toLowerCase() + formattedName.slice(1));
    }

    // Determine output path
    const outputDir = path.join(project.rootPath, project.structure[`${type}s`]);

    // Create directory if it doesn't exist
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Determine filename
    let filename;
    if (type === 'repository' || type === 'controller') {
      // Use camelCase for repositories and controllers
      filename = `${formattedName.charAt(0).toLowerCase() + formattedName.slice(1)}${type.charAt(0).toUpperCase() + type.slice(1)}${config.templates.extensions[type]}`;
    } else {
      // Use PascalCase for models and providers
      filename = `${formattedName}${config.templates.extensions[type]}`;
    }

    const outputPath = path.join(outputDir, filename);

    // Check if file already exists
    if (fs.existsSync(outputPath)) {
      logger.warn(`File already exists: ${outputPath}`);
      // Read existing file to avoid overwriting
      const existingContent = fs.readFileSync(outputPath, 'utf8');
      // Only write if content is different
      if (existingContent !== content) {
        // Create backup
        const backupPath = `${outputPath}.bak`;
        fs.writeFileSync(backupPath, existingContent);
        logger.info(`Created backup: ${backupPath}`);
        // Write new content
        fs.writeFileSync(outputPath, content);
      } else {
        logger.info(`File unchanged: ${outputPath}`);
      }
    } else {
      // Write file
      fs.writeFileSync(outputPath, content);
    }

    logger.info('Component generated', { projectId, type, name, outputPath });

    return {
      type,
      name: formattedName,
      path: outputPath
    };
  } catch (error) {
    logger.error('Error generating component', { error: error.message, projectId, type, name });
    throw error;
  }
}

// Start server
const PORT = process.env.PORT || config.port;
app.listen(PORT, () => {
  logger.info(`MCP Server running on port ${PORT}`);
});

module.exports = app;
