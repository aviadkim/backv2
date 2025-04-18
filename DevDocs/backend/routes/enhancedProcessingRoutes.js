/**
 * Enhanced Processing Routes
 *
 * This module provides API routes for the enhanced document processing pipeline.
 */

const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { spawn } = require('child_process');
const logger = require('../utils/logger');

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '..', '..', 'uploads');
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

/**
 * @route POST /api/enhanced/process
 * @desc Process a financial document with enhanced processing
 * @access Public
 */
router.post('/process', upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Get languages from request
    const languages = req.body.languages || ['eng', 'heb'];

    // Create task ID
    const taskId = uuidv4();

    // Create task entry
    tasks[taskId] = {
      taskId,
      status: 'processing',
      progress: 0,
      result: null,
      error: null,
      filePath: req.file.path,
      fileName: req.file.originalname
    };

    // Create output directory
    const outputDir = path.join(__dirname, '..', '..', 'processed', taskId);
    fs.mkdirSync(outputDir, { recursive: true });

    // Start processing in background
    processDocument(taskId, req.file.path, outputDir, languages);

    // Return task ID
    res.status(200).json({
      task_id: taskId,
      status: 'processing',
      progress: 0
    });
  } catch (error) {
    logger.error(`Error processing document: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

/**
 * @route GET /api/enhanced/status/:taskId
 * @desc Get the status of a processing task
 * @access Public
 */
router.get('/status/:taskId', (req, res) => {
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

/**
 * @route GET /api/enhanced/result/:taskId
 * @desc Get the result of a processing task
 * @access Public
 */
router.get('/result/:taskId', (req, res) => {
  const { taskId } = req.params;

  if (!tasks[taskId]) {
    return res.status(404).json({ error: 'Task not found' });
  }

  if (tasks[taskId].status !== 'completed') {
    return res.status(400).json({ error: `Task is not completed: ${tasks[taskId].status}` });
  }

  res.status(200).json(tasks[taskId].result);
});

/**
 * Process a document using the RAG Multimodal Processor
 *
 * @param {string} taskId - Task ID
 * @param {string} filePath - Path to the PDF file
 * @param {string} outputDir - Output directory
 * @param {string[]} languages - Languages for OCR
 */
function processDocument(taskId, filePath, outputDir, languages) {
  try {
    // Update task status
    tasks[taskId].status = 'processing';
    tasks[taskId].progress = 0.1;

    // Get API key from environment
    const apiKey = process.env.OPENAI_API_KEY || process.env.GOOGLE_API_KEY;

    // Create processor
    const RagMultimodalProcessor = require('../enhanced_processing/node_wrapper');
    const processor = new RagMultimodalProcessor({
      apiKey,
      languages,
      verbose: false
    });

    // Set progress callback
    processor.setProgressCallback((progress) => {
      tasks[taskId].progress = progress;
    });

    // Process document
    processor.process(filePath, outputDir)
      .then(result => {
        // Update task
        tasks[taskId].status = 'completed';
        tasks[taskId].progress = 1.0;
        tasks[taskId].result = result;

        logger.info(`Task ${taskId} completed successfully`);
      })
      .catch(error => {
        // Update task
        tasks[taskId].status = 'failed';
        tasks[taskId].error = error.message;

        logger.error(`Task ${taskId} failed: ${error.message}`);
      });
  } catch (error) {
    // Error starting process
    tasks[taskId].status = 'failed';
    tasks[taskId].error = error.message;

    logger.error(`Error starting processing: ${error.message}`);
  }
}

module.exports = router;
