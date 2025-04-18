/**
 * Performance Monitor
 * 
 * Monitors application performance and provides metrics.
 */

const os = require('os');
const logger = require('../../utils/logger');

// Performance metrics
let metrics = {
  requests: {
    total: 0,
    successful: 0,
    failed: 0,
    byEndpoint: {}
  },
  responseTime: {
    average: 0,
    min: Number.MAX_SAFE_INTEGER,
    max: 0,
    byEndpoint: {}
  },
  memory: {
    usage: [],
    average: 0,
    max: 0
  },
  cpu: {
    usage: [],
    average: 0,
    max: 0
  },
  errors: {
    count: 0,
    byType: {}
  },
  startTime: Date.now()
};

// Sampling interval in milliseconds
const SAMPLING_INTERVAL = 60000; // 1 minute

// Maximum number of samples to keep
const MAX_SAMPLES = 60; // 1 hour of data at 1-minute intervals

// Start monitoring
let monitoringInterval = null;

/**
 * Start performance monitoring
 * @returns {void}
 */
function startMonitoring() {
  if (monitoringInterval) {
    return;
  }
  
  logger.info('Starting performance monitoring');
  
  // Reset metrics
  metrics = {
    requests: {
      total: 0,
      successful: 0,
      failed: 0,
      byEndpoint: {}
    },
    responseTime: {
      average: 0,
      min: Number.MAX_SAFE_INTEGER,
      max: 0,
      byEndpoint: {}
    },
    memory: {
      usage: [],
      average: 0,
      max: 0
    },
    cpu: {
      usage: [],
      average: 0,
      max: 0
    },
    errors: {
      count: 0,
      byType: {}
    },
    startTime: Date.now()
  };
  
  // Start monitoring interval
  monitoringInterval = setInterval(collectMetrics, SAMPLING_INTERVAL);
  
  // Collect initial metrics
  collectMetrics();
}

/**
 * Stop performance monitoring
 * @returns {void}
 */
function stopMonitoring() {
  if (!monitoringInterval) {
    return;
  }
  
  logger.info('Stopping performance monitoring');
  
  clearInterval(monitoringInterval);
  monitoringInterval = null;
}

/**
 * Collect performance metrics
 * @returns {void}
 */
function collectMetrics() {
  try {
    // Collect memory usage
    const memoryUsage = process.memoryUsage();
    const heapUsedMB = Math.round(memoryUsage.heapUsed / 1024 / 1024 * 100) / 100;
    
    metrics.memory.usage.push({
      timestamp: Date.now(),
      value: heapUsedMB
    });
    
    // Limit number of samples
    if (metrics.memory.usage.length > MAX_SAMPLES) {
      metrics.memory.usage.shift();
    }
    
    // Update memory stats
    metrics.memory.average = calculateAverage(metrics.memory.usage.map(sample => sample.value));
    metrics.memory.max = Math.max(...metrics.memory.usage.map(sample => sample.value));
    
    // Collect CPU usage
    const cpuUsage = os.loadavg()[0]; // 1-minute load average
    
    metrics.cpu.usage.push({
      timestamp: Date.now(),
      value: cpuUsage
    });
    
    // Limit number of samples
    if (metrics.cpu.usage.length > MAX_SAMPLES) {
      metrics.cpu.usage.shift();
    }
    
    // Update CPU stats
    metrics.cpu.average = calculateAverage(metrics.cpu.usage.map(sample => sample.value));
    metrics.cpu.max = Math.max(...metrics.cpu.usage.map(sample => sample.value));
    
    logger.debug('Performance metrics collected', {
      memory: {
        current: heapUsedMB,
        average: metrics.memory.average,
        max: metrics.memory.max
      },
      cpu: {
        current: cpuUsage,
        average: metrics.cpu.average,
        max: metrics.cpu.max
      }
    });
  } catch (error) {
    logger.error(`Error collecting performance metrics: ${error.message}`, error);
  }
}

/**
 * Record request metrics
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {number} startTime - Request start time
 * @returns {void}
 */
function recordRequest(req, res, startTime) {
  try {
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    const endpoint = `${req.method} ${req.originalUrl.split('?')[0]}`;
    const statusCode = res.statusCode;
    const isSuccess = statusCode < 400;
    
    // Update request counts
    metrics.requests.total++;
    
    if (isSuccess) {
      metrics.requests.successful++;
    } else {
      metrics.requests.failed++;
    }
    
    // Update endpoint-specific counts
    if (!metrics.requests.byEndpoint[endpoint]) {
      metrics.requests.byEndpoint[endpoint] = {
        total: 0,
        successful: 0,
        failed: 0
      };
    }
    
    metrics.requests.byEndpoint[endpoint].total++;
    
    if (isSuccess) {
      metrics.requests.byEndpoint[endpoint].successful++;
    } else {
      metrics.requests.byEndpoint[endpoint].failed++;
    }
    
    // Update response time metrics
    metrics.responseTime.min = Math.min(metrics.responseTime.min, responseTime);
    metrics.responseTime.max = Math.max(metrics.responseTime.max, responseTime);
    
    // Calculate new average response time
    const totalRequests = metrics.requests.total;
    const currentAverage = metrics.responseTime.average;
    metrics.responseTime.average = ((currentAverage * (totalRequests - 1)) + responseTime) / totalRequests;
    
    // Update endpoint-specific response time metrics
    if (!metrics.responseTime.byEndpoint[endpoint]) {
      metrics.responseTime.byEndpoint[endpoint] = {
        average: 0,
        min: Number.MAX_SAFE_INTEGER,
        max: 0,
        count: 0
      };
    }
    
    const endpointMetrics = metrics.responseTime.byEndpoint[endpoint];
    endpointMetrics.min = Math.min(endpointMetrics.min, responseTime);
    endpointMetrics.max = Math.max(endpointMetrics.max, responseTime);
    endpointMetrics.count++;
    
    // Calculate new average response time for endpoint
    const currentEndpointAverage = endpointMetrics.average;
    endpointMetrics.average = ((currentEndpointAverage * (endpointMetrics.count - 1)) + responseTime) / endpointMetrics.count;
    
    logger.debug('Request recorded', {
      endpoint,
      statusCode,
      responseTime,
      isSuccess
    });
  } catch (error) {
    logger.error(`Error recording request metrics: ${error.message}`, error);
  }
}

/**
 * Record error
 * @param {Error} error - Error object
 * @returns {void}
 */
function recordError(error) {
  try {
    metrics.errors.count++;
    
    const errorType = error.name || 'Unknown';
    
    if (!metrics.errors.byType[errorType]) {
      metrics.errors.byType[errorType] = 0;
    }
    
    metrics.errors.byType[errorType]++;
    
    logger.debug('Error recorded', {
      errorType,
      message: error.message
    });
  } catch (err) {
    logger.error(`Error recording error metrics: ${err.message}`, err);
  }
}

/**
 * Get performance metrics
 * @returns {Object} - Performance metrics
 */
function getMetrics() {
  return {
    ...metrics,
    uptime: Date.now() - metrics.startTime
  };
}

/**
 * Reset performance metrics
 * @returns {void}
 */
function resetMetrics() {
  logger.info('Resetting performance metrics');
  
  metrics = {
    requests: {
      total: 0,
      successful: 0,
      failed: 0,
      byEndpoint: {}
    },
    responseTime: {
      average: 0,
      min: Number.MAX_SAFE_INTEGER,
      max: 0,
      byEndpoint: {}
    },
    memory: {
      usage: [],
      average: 0,
      max: 0
    },
    cpu: {
      usage: [],
      average: 0,
      max: 0
    },
    errors: {
      count: 0,
      byType: {}
    },
    startTime: Date.now()
  };
}

/**
 * Calculate average of an array of numbers
 * @param {number[]} values - Array of numbers
 * @returns {number} - Average
 * @private
 */
function calculateAverage(values) {
  if (!values.length) {
    return 0;
  }
  
  const sum = values.reduce((acc, val) => acc + val, 0);
  return Math.round((sum / values.length) * 100) / 100;
}

/**
 * Create performance monitoring middleware
 * @returns {Function} - Express middleware
 */
function performanceMiddleware() {
  return (req, res, next) => {
    const startTime = Date.now();
    
    // Record response
    res.on('finish', () => {
      recordRequest(req, res, startTime);
    });
    
    next();
  };
}

module.exports = {
  startMonitoring,
  stopMonitoring,
  recordRequest,
  recordError,
  getMetrics,
  resetMetrics,
  performanceMiddleware
};
