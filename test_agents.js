/**
 * Test script for financial agents
 */

// Import required modules
const fs = require('fs');
const path = require('path');

// Define the agents to test
const agents = [
  { name: 'FinancialAdvisorAgent', jsFile: 'FinancialAdvisorAgent.js', pyFile: 'financial_advisor_agent.py' },
  { name: 'FinancialDataAnalyzerAgent', jsFile: 'FinancialDataAnalyzerAgent.js', pyFile: 'financial_data_analyzer_agent.py' },
  { name: 'FinancialTableDetectorAgent', jsFile: 'FinancialTableDetectorAgent.js', pyFile: 'financial_table_detector_agent.py' },
  { name: 'QueryEngineAgent', jsFile: 'QueryEngineAgent.js', pyFile: 'query_engine_agent.py' },
  { name: 'DocumentComparisonAgent', jsFile: 'DocumentComparisonAgent.js', pyFile: 'document_comparison_agent.py' },
  { name: 'ISINExtractorAgent', jsFile: 'ISINExtractorAgent.js', pyFile: 'isin_extractor_agent.py' },
  { name: 'DocumentPreprocessorAgent', jsFile: 'DocumentPreprocessorAgent.js', pyFile: 'document_preprocessor_agent.py' },
  { name: 'DocumentMergeAgent', jsFile: 'DocumentMergeAgent.js', pyFile: 'document_merge_agent.py' },
  { name: 'HebrewOCRAgent', jsFile: 'HebrewOCRAgent.js', pyFile: 'hebrew_ocr_agent.py' }
];

// Check if the agents exist
console.log('Checking if agents exist...');
const agentDir = path.join(__dirname, 'DevDocs', 'backend', 'agents');

let allAgentsExist = true;
for (const agent of agents) {
  const jsPath = path.join(agentDir, agent.jsFile);
  const pyPath = path.join(agentDir, agent.pyFile);

  const jsExists = fs.existsSync(jsPath);
  const pyExists = fs.existsSync(pyPath);

  if (jsExists || pyExists) {
    console.log(`✅ ${agent.name} exists (${jsExists ? 'JS' : ''}${jsExists && pyExists ? ' & ' : ''}${pyExists ? 'Python' : ''})`);
  } else {
    console.log(`❌ ${agent.name} does not exist in either JS or Python`);
    allAgentsExist = false;
  }
}

// Check if the controllers exist
console.log('\nChecking if controllers exist...');
const controllerDir = path.join(__dirname, 'DevDocs', 'backend', 'controllers');

const controllers = [
  'advisorController.js',
  'financialController.js',
  'queryController.js',
  'comparisonController.js',
  'exportController.js',
  'ocrController.js'
];

let allControllersExist = true;
for (const controller of controllers) {
  const controllerPath = path.join(controllerDir, controller);
  if (fs.existsSync(controllerPath)) {
    console.log(`✅ ${controller} exists`);
  } else {
    console.log(`❌ ${controller} does not exist`);
    allControllersExist = false;
  }
}

// Check if the routes exist
console.log('\nChecking if routes exist...');
const routeDir = path.join(__dirname, 'DevDocs', 'backend', 'routes', 'api');

const routes = [
  'advisor.js',
  'financial.js',
  'query.js',
  'comparison.js',
  'export.js',
  'ocr.js'
];

let allRoutesExist = true;
for (const route of routes) {
  const routePath = path.join(routeDir, route);
  if (fs.existsSync(routePath)) {
    console.log(`✅ ${route} exists`);
  } else {
    console.log(`❌ ${route} does not exist`);
    allRoutesExist = false;
  }
}

// Check if the services exist
console.log('\nChecking if services exist...');
const serviceDir = path.join(__dirname, 'DevDocs', 'backend', 'services');

const services = [
  'ai/openRouterService.js',
  'export/dataExportService.js',
  'storage/supabaseStorageService.js'
];

let allServicesExist = true;
for (const service of services) {
  const servicePath = path.join(serviceDir, service);
  if (fs.existsSync(servicePath)) {
    console.log(`✅ ${service} exists`);
  } else {
    console.log(`❌ ${service} does not exist`);
    allServicesExist = false;
  }
}

// Print summary
console.log('\nSummary:');
console.log(`Agents: ${allAgentsExist ? '✅ All exist' : '❌ Some missing'}`);
console.log(`Controllers: ${allControllersExist ? '✅ All exist' : '❌ Some missing'}`);
console.log(`Routes: ${allRoutesExist ? '✅ All exist' : '❌ Some missing'}`);
console.log(`Services: ${allServicesExist ? '✅ All exist' : '❌ Some missing'}`);

// Overall status
if (allAgentsExist && allControllersExist && allRoutesExist && allServicesExist) {
  console.log('\n✅ All components exist and are ready for testing!');
} else {
  console.log('\n❌ Some components are missing. Please check the logs above.');
}
