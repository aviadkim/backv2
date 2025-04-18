/**
 * Express server for the RAG Multimodal Financial Document Processor API.
 */

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const RagMultimodalProcessor = require('./node_wrapper');

// Create Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, 'uploads');
    fs.mkdirSync(uploadDir, { recursive: true });
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  }
});

// Store processing tasks
const tasks = {};

// Serve static files
app.use(express.static('public'));
app.use('/output', express.static('output'));

// Parse JSON body
app.use(express.json());

// API routes
app.post('/api/process', upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Get languages from request
    const languages = req.body.languages ? req.body.languages.split(',') : ['eng', 'heb'];
    
    // Create task ID
    const taskId = uuidv4();
    
    // Create output directory
    const outputDir = path.join(__dirname, 'output', taskId);
    fs.mkdirSync(outputDir, { recursive: true });
    
    // Create task entry
    tasks[taskId] = {
      taskId,
      status: 'processing',
      progress: 0,
      result: null,
      error: null,
      filePath: req.file.path,
      fileName: req.file.originalname,
      outputDir
    };
    
    // Get API key from environment or request
    const apiKey = process.env.OPENAI_API_KEY || process.env.GOOGLE_API_KEY;
    
    // Create processor
    const processor = new RagMultimodalProcessor({
      apiKey,
      languages,
      verbose: false
    });
    
    // Set progress callback
    processor.setProgressCallback((progress) => {
      tasks[taskId].progress = progress;
    });
    
    // Process document in background
    processor.process(req.file.path, outputDir)
      .then(result => {
        tasks[taskId].status = 'completed';
        tasks[taskId].progress = 1.0;
        tasks[taskId].result = result;
        
        console.log(`Task ${taskId} completed successfully`);
      })
      .catch(error => {
        tasks[taskId].status = 'failed';
        tasks[taskId].error = error.message;
        
        console.error(`Task ${taskId} failed: ${error.message}`);
      });
    
    // Return task ID
    res.status(200).json({
      task_id: taskId,
      status: 'processing',
      progress: 0
    });
  } catch (error) {
    console.error(`Error processing document: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/status/:taskId', (req, res) => {
  const { taskId } = req.params;
  
  if (!tasks[taskId]) {
    return res.status(404).json({ error: 'Task not found' });
  }
  
  res.status(200).json({
    task_id: taskId,
    status: tasks[taskId].status,
    progress: tasks[taskId].progress,
    error: tasks[taskId].error
  });
});

app.get('/api/result/:taskId', (req, res) => {
  const { taskId } = req.params;
  
  if (!tasks[taskId]) {
    return res.status(404).json({ error: 'Task not found' });
  }
  
  if (tasks[taskId].status !== 'completed') {
    return res.status(400).json({ error: `Task is not completed: ${tasks[taskId].status}` });
  }
  
  res.status(200).json(tasks[taskId].result);
});

app.get('/api/visualizations/:taskId', (req, res) => {
  const { taskId } = req.params;
  
  if (!tasks[taskId]) {
    return res.status(404).json({ error: 'Task not found' });
  }
  
  const visualizationsDir = path.join(tasks[taskId].outputDir, 'visualizations');
  
  if (!fs.existsSync(visualizationsDir)) {
    return res.status(404).json({ error: 'Visualizations not found' });
  }
  
  // Get list of visualization files
  const files = fs.readdirSync(visualizationsDir)
    .filter(file => file.endsWith('.png'))
    .map(file => `/output/${taskId}/visualizations/${file}`);
  
  res.status(200).json({ files });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
