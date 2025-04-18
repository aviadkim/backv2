/**
 * Performance Routes
 * 
 * API routes for performance monitoring and optimization.
 */

const express = require('express');
const router = express.Router();
const { authenticate, authorizeRole } = require('../../../middleware/authMiddleware');
const performanceMonitor = require('../../../services/performance/performanceMonitor');
const cacheService = require('../../../services/cache/cacheService');
const logger = require('../../../utils/logger');

/**
 * @route GET /api/performance/metrics
 * @desc Get performance metrics
 * @access Private (Admin only)
 */
router.get('/metrics', authenticate, authorizeRole(['admin']), (req, res) => {
  try {
    const metrics = performanceMonitor.getMetrics();
    
    return res.status(200).json(metrics);
  } catch (error) {
    logger.error(`Error getting performance metrics: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to get performance metrics' });
  }
});

/**
 * @route POST /api/performance/metrics/reset
 * @desc Reset performance metrics
 * @access Private (Admin only)
 */
router.post('/metrics/reset', authenticate, authorizeRole(['admin']), (req, res) => {
  try {
    performanceMonitor.resetMetrics();
    
    return res.status(200).json({ message: 'Performance metrics reset successfully' });
  } catch (error) {
    logger.error(`Error resetting performance metrics: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to reset performance metrics' });
  }
});

/**
 * @route GET /api/performance/cache/stats
 * @desc Get cache statistics
 * @access Private (Admin only)
 */
router.get('/cache/stats', authenticate, authorizeRole(['admin']), (req, res) => {
  try {
    const stats = cacheService.getStats();
    const size = cacheService.size();
    const keys = cacheService.keys();
    
    return res.status(200).json({
      stats,
      size,
      keys
    });
  } catch (error) {
    logger.error(`Error getting cache statistics: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to get cache statistics' });
  }
});

/**
 * @route POST /api/performance/cache/flush
 * @desc Flush cache
 * @access Private (Admin only)
 */
router.post('/cache/flush', authenticate, authorizeRole(['admin']), (req, res) => {
  try {
    cacheService.flush();
    
    return res.status(200).json({ message: 'Cache flushed successfully' });
  } catch (error) {
    logger.error(`Error flushing cache: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to flush cache' });
  }
});

/**
 * @route DELETE /api/performance/cache/keys/:key
 * @desc Delete cache key
 * @access Private (Admin only)
 */
router.delete('/cache/keys/:key', authenticate, authorizeRole(['admin']), (req, res) => {
  try {
    const { key } = req.params;
    const deleted = cacheService.del(key);
    
    if (deleted) {
      return res.status(200).json({ message: `Cache key '${key}' deleted successfully` });
    } else {
      return res.status(404).json({ error: `Cache key '${key}' not found` });
    }
  } catch (error) {
    logger.error(`Error deleting cache key: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to delete cache key' });
  }
});

module.exports = router;
