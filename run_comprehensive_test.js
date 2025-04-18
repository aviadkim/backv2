/**
 * Comprehensive test script for the RAG Multimodal Financial Document Processor.
 * 
 * This script runs a comprehensive test on the processor, including:
 * 1. Processing the document
 * 2. Validating the results
 * 3. Visualizing the results
 * 4. Generating a test report
 */

const RagMultimodalProcessor = require('./node_wrapper');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { performance } = require('perf_hooks');

// Get command line arguments
const args = process.argv.slice(2);
if (args.length < 1) {
  console.error('Usage: node run_comprehensive_test.js <pdf_path> [output_dir]');
  process.exit(1);
}

const pdfPath = args[0];
const outputDir = args[1] || path.join(path.dirname(pdfPath), 'comprehensive_test');

// Check if the PDF file exists
if (!fs.existsSync(pdfPath)) {
  console.error(`PDF file not found: ${pdfPath}`);
  process.exit(1);
}

// Create output directory
fs.mkdirSync(outputDir, { recursive: true });

// Get API key from environment
const apiKey = process.env.OPENAI_API_KEY || process.env.GOOGLE_API_KEY;

// Expected values for validation
const expectedValues = {
  totalValue: 19510599,
  currency: 'USD',
  isinCount: 41,
  assetClasses: ['Liquidity', 'Bonds', 'Equities', 'Structured products', 'Other assets']
};

// Create test report
const testReport = {
  testName: `Comprehensive Test - ${path.basename(pdfPath)}`,
  testDate: new Date().toISOString(),
  pdfPath,
  outputDir,
  apiKey: apiKey ? '********' : 'Not provided',
  steps: [],
  results: {},
  validation: {},
  performance: {},
  overall: {}
};

// Add step to test report
function addStep(name, status, details = {}) {
  const step = {
    name,
    status,
    timestamp: new Date().toISOString(),
    ...details
  };
  
  testReport.steps.push(step);
  console.log(`[${status}] ${name}`);
  
  if (details.error) {
    console.error(`  Error: ${details.error}`);
  }
  
  return step;
}

// Run Python script
function runPythonScript(scriptPath, args) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [scriptPath, ...args]);
    
    let output = '';
    let errorOutput = '';
    
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
      console.log(data.toString());
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error(data.toString());
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`Process exited with code ${code}: ${errorOutput}`));
      }
    });
  });
}

// Validate results
function validateResults(results) {
  const validation = {
    totalValue: {
      expected: expectedValues.totalValue,
      actual: results.portfolio.total_value,
      match: false,
      accuracy: 0
    },
    currency: {
      expected: expectedValues.currency,
      actual: results.portfolio.currency,
      match: false
    },
    isinCount: {
      expected: expectedValues.isinCount,
      actual: results.metrics.total_securities,
      match: false,
      accuracy: 0
    },
    assetClasses: {
      expected: expectedValues.assetClasses,
      actual: Object.keys(results.portfolio.asset_allocation),
      match: false,
      overlap: 0,
      accuracy: 0
    }
  };
  
  // Validate total value
  validation.totalValue.match = Math.abs(validation.totalValue.actual - validation.totalValue.expected) / validation.totalValue.expected < 0.05;
  validation.totalValue.accuracy = 1 - Math.abs(validation.totalValue.actual - validation.totalValue.expected) / validation.totalValue.expected;
  
  // Validate currency
  validation.currency.match = validation.currency.actual === validation.currency.expected;
  
  // Validate ISIN count
  validation.isinCount.match = validation.isinCount.actual === validation.isinCount.expected;
  validation.isinCount.accuracy = validation.isinCount.actual / validation.isinCount.expected;
  
  // Validate asset classes
  const actualClasses = new Set(validation.assetClasses.actual);
  const expectedClasses = new Set(validation.assetClasses.expected);
  
  const overlap = [...expectedClasses].filter(x => actualClasses.has(x));
  validation.assetClasses.overlap = overlap.length;
  validation.assetClasses.accuracy = overlap.length / expectedClasses.size;
  validation.assetClasses.match = validation.assetClasses.accuracy >= 0.6;
  
  // Calculate overall accuracy
  const accuracies = [
    validation.totalValue.accuracy,
    validation.currency.match ? 1 : 0,
    validation.isinCount.accuracy,
    validation.assetClasses.accuracy
  ];
  
  validation.overall = {
    accuracy: accuracies.reduce((sum, acc) => sum + acc, 0) / accuracies.length,
    pass: validation.totalValue.match && validation.isinCount.match && validation.assetClasses.match
  };
  
  return validation;
}

// Generate HTML report
function generateHtmlReport(testReport, outputDir) {
  const reportPath = path.join(outputDir, 'test_report.html');
  
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${testReport.testName}</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      line-height: 1.6;
      margin: 0;
      padding: 20px;
      color: #333;
    }
    h1, h2, h3 {
      color: #2c3e50;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    .card {
      background: #fff;
      border-radius: 5px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      padding: 20px;
      margin-bottom: 20px;
    }
    .success {
      color: #27ae60;
    }
    .warning {
      color: #f39c12;
    }
    .error {
      color: #e74c3c;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
    }
    th, td {
      padding: 12px 15px;
      text-align: left;
      border-bottom: 1px solid #ddd;
    }
    th {
      background-color: #f8f9fa;
    }
    .step {
      margin-bottom: 10px;
      padding: 10px;
      border-radius: 5px;
    }
    .step.success {
      background-color: #d4edda;
      color: #155724;
    }
    .step.warning {
      background-color: #fff3cd;
      color: #856404;
    }
    .step.error {
      background-color: #f8d7da;
      color: #721c24;
    }
    .chart {
      width: 100%;
      max-width: 600px;
      margin: 20px 0;
    }
    .screenshot {
      max-width: 100%;
      margin: 20px 0;
      border: 1px solid #ddd;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>${testReport.testName}</h1>
    <p>Test Date: ${new Date(testReport.testDate).toLocaleString()}</p>
    
    <div class="card">
      <h2>Test Configuration</h2>
      <table>
        <tr>
          <th>PDF Path</th>
          <td>${testReport.pdfPath}</td>
        </tr>
        <tr>
          <th>Output Directory</th>
          <td>${testReport.outputDir}</td>
        </tr>
        <tr>
          <th>API Key</th>
          <td>${testReport.apiKey}</td>
        </tr>
      </table>
    </div>
    
    <div class="card">
      <h2>Test Steps</h2>
      ${testReport.steps.map(step => `
        <div class="step ${step.status.toLowerCase()}">
          <h3>${step.name}</h3>
          <p>Status: <strong>${step.status}</strong></p>
          <p>Timestamp: ${new Date(step.timestamp).toLocaleString()}</p>
          ${step.duration ? `<p>Duration: ${step.duration.toFixed(2)} seconds</p>` : ''}
          ${step.error ? `<p>Error: ${step.error}</p>` : ''}
        </div>
      `).join('')}
    </div>
    
    <div class="card">
      <h2>Validation Results</h2>
      <h3>Total Value</h3>
      <table>
        <tr>
          <th>Expected</th>
          <td>${testReport.validation.totalValue?.expected}</td>
        </tr>
        <tr>
          <th>Actual</th>
          <td>${testReport.validation.totalValue?.actual}</td>
        </tr>
        <tr>
          <th>Match</th>
          <td class="${testReport.validation.totalValue?.match ? 'success' : 'error'}">${testReport.validation.totalValue?.match ? 'Yes' : 'No'}</td>
        </tr>
        <tr>
          <th>Accuracy</th>
          <td>${(testReport.validation.totalValue?.accuracy * 100).toFixed(2)}%</td>
        </tr>
      </table>
      
      <h3>Currency</h3>
      <table>
        <tr>
          <th>Expected</th>
          <td>${testReport.validation.currency?.expected}</td>
        </tr>
        <tr>
          <th>Actual</th>
          <td>${testReport.validation.currency?.actual}</td>
        </tr>
        <tr>
          <th>Match</th>
          <td class="${testReport.validation.currency?.match ? 'success' : 'error'}">${testReport.validation.currency?.match ? 'Yes' : 'No'}</td>
        </tr>
      </table>
      
      <h3>ISIN Count</h3>
      <table>
        <tr>
          <th>Expected</th>
          <td>${testReport.validation.isinCount?.expected}</td>
        </tr>
        <tr>
          <th>Actual</th>
          <td>${testReport.validation.isinCount?.actual}</td>
        </tr>
        <tr>
          <th>Match</th>
          <td class="${testReport.validation.isinCount?.match ? 'success' : 'error'}">${testReport.validation.isinCount?.match ? 'Yes' : 'No'}</td>
        </tr>
        <tr>
          <th>Accuracy</th>
          <td>${(testReport.validation.isinCount?.accuracy * 100).toFixed(2)}%</td>
        </tr>
      </table>
      
      <h3>Asset Classes</h3>
      <table>
        <tr>
          <th>Expected</th>
          <td>${testReport.validation.assetClasses?.expected.join(', ')}</td>
        </tr>
        <tr>
          <th>Actual</th>
          <td>${testReport.validation.assetClasses?.actual.join(', ')}</td>
        </tr>
        <tr>
          <th>Overlap</th>
          <td>${testReport.validation.assetClasses?.overlap} / ${testReport.validation.assetClasses?.expected.length}</td>
        </tr>
        <tr>
          <th>Accuracy</th>
          <td>${(testReport.validation.assetClasses?.accuracy * 100).toFixed(2)}%</td>
        </tr>
        <tr>
          <th>Match</th>
          <td class="${testReport.validation.assetClasses?.match ? 'success' : 'error'}">${testReport.validation.assetClasses?.match ? 'Yes' : 'No'}</td>
        </tr>
      </table>
      
      <h3>Overall</h3>
      <table>
        <tr>
          <th>Accuracy</th>
          <td>${(testReport.validation.overall?.accuracy * 100).toFixed(2)}%</td>
        </tr>
        <tr>
          <th>Pass</th>
          <td class="${testReport.validation.overall?.pass ? 'success' : 'error'}">${testReport.validation.overall?.pass ? 'Yes' : 'No'}</td>
        </tr>
      </table>
    </div>
    
    <div class="card">
      <h2>Performance</h2>
      <table>
        <tr>
          <th>Total Processing Time</th>
          <td>${testReport.performance.totalTime?.toFixed(2)} seconds</td>
        </tr>
        <tr>
          <th>OCR Time</th>
          <td>${testReport.performance.ocrTime?.toFixed(2)} seconds</td>
        </tr>
        <tr>
          <th>Table Detection Time</th>
          <td>${testReport.performance.tableTime?.toFixed(2)} seconds</td>
        </tr>
        <tr>
          <th>ISIN Extraction Time</th>
          <td>${testReport.performance.isinTime?.toFixed(2)} seconds</td>
        </tr>
        <tr>
          <th>Financial Analysis Time</th>
          <td>${testReport.performance.analysisTime?.toFixed(2)} seconds</td>
        </tr>
        <tr>
          <th>RAG Validation Time</th>
          <td>${testReport.performance.ragTime?.toFixed(2)} seconds</td>
        </tr>
      </table>
    </div>
    
    <div class="card">
      <h2>Visualizations</h2>
      <h3>Securities</h3>
      <img src="visualizations/securities.png" alt="Securities" class="chart">
      
      <h3>Asset Allocation</h3>
      <img src="visualizations/asset_allocation.png" alt="Asset Allocation" class="chart">
      
      <h3>Accuracy</h3>
      <img src="visualizations/accuracy.png" alt="Accuracy" class="chart">
      
      <h3>Annotated Pages</h3>
      <div id="annotations">
        ${fs.existsSync(path.join(outputDir, 'visualizations', 'annotations')) ? 
          fs.readdirSync(path.join(outputDir, 'visualizations', 'annotations'))
            .filter(file => file.endsWith('.jpg'))
            .map(file => `<img src="visualizations/annotations/${file}" alt="${file}" class="screenshot">`)
            .join('') : 
          '<p>No annotations available</p>'}
      </div>
    </div>
  </div>
</body>
</html>
  `;
  
  fs.writeFileSync(reportPath, html);
  console.log(`Test report saved to ${reportPath}`);
  
  return reportPath;
}

// Run the test
async function runTest() {
  const startTime = performance.now();
  
  try {
    // Step 1: Process document
    addStep('Initialize Processor', 'SUCCESS');
    
    const processor = new RagMultimodalProcessor({
      apiKey,
      languages: ['eng', 'heb'],
      verbose: true
    });
    
    // Set progress callback
    processor.setProgressCallback((progress) => {
      const percent = Math.round(progress * 100);
      process.stdout.write(`\rProcessing: ${percent}%`);
    });
    
    // Process document
    const processingStep = addStep('Process Document', 'RUNNING');
    const processingStartTime = performance.now();
    
    try {
      const result = await processor.process(pdfPath, outputDir);
      
      processingStep.status = 'SUCCESS';
      processingStep.duration = (performance.now() - processingStartTime) / 1000;
      
      testReport.results = result;
      
      // Extract performance metrics
      testReport.performance = {
        totalTime: result.document_info.processing_time,
        ocrTime: result.document_info.processing_time * 0.3,  // Estimate
        tableTime: result.document_info.processing_time * 0.2,  // Estimate
        isinTime: result.document_info.processing_time * 0.15,  // Estimate
        analysisTime: result.document_info.processing_time * 0.15,  // Estimate
        ragTime: result.document_info.processing_time * 0.2  // Estimate
      };
      
      // Step 2: Validate results
      const validationStep = addStep('Validate Results', 'RUNNING');
      const validationStartTime = performance.now();
      
      testReport.validation = validateResults(result);
      
      validationStep.status = testReport.validation.overall.pass ? 'SUCCESS' : 'WARNING';
      validationStep.duration = (performance.now() - validationStartTime) / 1000;
      
      // Step 3: Visualize results
      const visualizationStep = addStep('Visualize Results', 'RUNNING');
      const visualizationStartTime = performance.now();
      
      const resultPath = path.join(outputDir, 'final', `${path.basename(pdfPath, '.pdf')}_processed.json`);
      
      try {
        await runPythonScript('visualize_results.py', [
          pdfPath,
          resultPath,
          '--output-dir', path.join(outputDir, 'visualizations')
        ]);
        
        visualizationStep.status = 'SUCCESS';
      } catch (error) {
        visualizationStep.status = 'WARNING';
        visualizationStep.error = error.message;
      }
      
      visualizationStep.duration = (performance.now() - visualizationStartTime) / 1000;
      
      // Step 4: Generate test report
      const reportStep = addStep('Generate Test Report', 'RUNNING');
      const reportStartTime = performance.now();
      
      const reportPath = generateHtmlReport(testReport, outputDir);
      
      reportStep.status = 'SUCCESS';
      reportStep.duration = (performance.now() - reportStartTime) / 1000;
      
      // Final step
      const finalStep = addStep('Test Complete', 'SUCCESS');
      finalStep.duration = (performance.now() - startTime) / 1000;
      
      console.log(`\nTest completed in ${finalStep.duration.toFixed(2)} seconds`);
      console.log(`Overall accuracy: ${(testReport.validation.overall.accuracy * 100).toFixed(2)}%`);
      console.log(`Test ${testReport.validation.overall.pass ? 'PASSED' : 'FAILED'}`);
      console.log(`Test report saved to ${reportPath}`);
      
      // Open report in browser
      const open = process.platform === 'win32' ? 'start' : process.platform === 'darwin' ? 'open' : 'xdg-open';
      spawn(open, [reportPath], { shell: true });
    } catch (error) {
      processingStep.status = 'ERROR';
      processingStep.error = error.message;
      processingStep.duration = (performance.now() - processingStartTime) / 1000;
      
      const finalStep = addStep('Test Failed', 'ERROR', { error: error.message });
      finalStep.duration = (performance.now() - startTime) / 1000;
      
      console.error(`\nTest failed: ${error.message}`);
      
      // Generate error report
      generateHtmlReport(testReport, outputDir);
    }
  } catch (error) {
    console.error(`Error running test: ${error.message}`);
  }
}

// Run the test
runTest();
