/**
 * Security Routes
 * 
 * API routes for security and compliance features.
 */

const express = require('express');
const router = express.Router();
const { authenticate, authorizeRole } = require('../../../middleware/authMiddleware');
const encryptionService = require('../../../services/security/encryptionService');
const auditService = require('../../../services/security/auditService');
const dataRetentionService = require('../../../services/security/dataRetentionService');
const gdprService = require('../../../services/security/gdprService');
const logger = require('../../../utils/logger');

/**
 * @route GET /api/security/audit-logs
 * @desc Get audit logs
 * @access Private (Admin only)
 */
router.get('/audit-logs', authenticate, authorizeRole(['admin']), async (req, res) => {
  try {
    const options = {
      eventType: req.query.eventType,
      action: req.query.action,
      userId: req.query.userId,
      startDate: req.query.startDate,
      endDate: req.query.endDate,
      limit: req.query.limit,
      offset: req.query.offset
    };
    
    const auditLogs = await auditService.getAuditLogs(options);
    
    // Log access to audit logs
    await auditService.logAccessEvent('view_audit_logs', {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      query: req.query
    }, req.user);
    
    return res.status(200).json({
      count: auditLogs.length,
      logs: auditLogs
    });
  } catch (error) {
    logger.error(`Error getting audit logs: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to get audit logs' });
  }
});

/**
 * @route GET /api/security/retention-policies
 * @desc Get data retention policies
 * @access Private (Admin only)
 */
router.get('/retention-policies', authenticate, authorizeRole(['admin']), (req, res) => {
  try {
    const policies = dataRetentionService.getRetentionPolicies();
    
    // Log access to retention policies
    auditService.logAccessEvent('view_retention_policies', {
      ip: req.ip,
      userAgent: req.get('User-Agent')
    }, req.user);
    
    return res.status(200).json(policies);
  } catch (error) {
    logger.error(`Error getting retention policies: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to get retention policies' });
  }
});

/**
 * @route PUT /api/security/retention-policies
 * @desc Update data retention policies
 * @access Private (Admin only)
 */
router.put('/retention-policies', authenticate, authorizeRole(['admin']), (req, res) => {
  try {
    const { documents, auditLogs, userActivity, temporaryFiles } = req.body;
    
    const policies = dataRetentionService.updateRetentionPolicies({
      documents,
      auditLogs,
      userActivity,
      temporaryFiles
    });
    
    // Log update to retention policies
    auditService.logAdminEvent('update_retention_policies', {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      policies
    }, req.user);
    
    return res.status(200).json(policies);
  } catch (error) {
    logger.error(`Error updating retention policies: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to update retention policies' });
  }
});

/**
 * @route POST /api/security/cleanup
 * @desc Clean up expired data
 * @access Private (Admin only)
 */
router.post('/cleanup', authenticate, authorizeRole(['admin']), async (req, res) => {
  try {
    const options = req.body;
    
    const results = await dataRetentionService.cleanupExpiredData(options);
    
    // Log data cleanup
    auditService.logAdminEvent('cleanup_expired_data', {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      options,
      results
    }, req.user);
    
    return res.status(200).json(results);
  } catch (error) {
    logger.error(`Error cleaning up expired data: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to clean up expired data' });
  }
});

/**
 * @route GET /api/security/data-export/:userId
 * @desc Export user data (GDPR)
 * @access Private (Admin or own user)
 */
router.get('/data-export/:userId', authenticate, async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Check if user is authorized to export this data
    if (req.user.role !== 'admin' && req.user.id !== userId) {
      return res.status(403).json({ error: 'Unauthorized to export this user data' });
    }
    
    const result = await gdprService.exportUserData(userId);
    
    // Log data export
    auditService.logDataEvent('export_user_data', {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId,
      exportResult: result
    }, req.user);
    
    return res.status(200).json(result);
  } catch (error) {
    logger.error(`Error exporting user data: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to export user data' });
  }
});

/**
 * @route DELETE /api/security/user-data/:userId
 * @desc Delete user data (GDPR)
 * @access Private (Admin only)
 */
router.delete('/user-data/:userId', authenticate, authorizeRole(['admin']), async (req, res) => {
  try {
    const { userId } = req.params;
    
    const result = await gdprService.deleteUserData(userId);
    
    // Log data deletion
    auditService.logDataEvent('delete_user_data', {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId,
      deletionResult: result
    }, req.user);
    
    return res.status(200).json(result);
  } catch (error) {
    logger.error(`Error deleting user data: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to delete user data' });
  }
});

/**
 * @route POST /api/security/anonymize/:userId
 * @desc Anonymize user data (GDPR)
 * @access Private (Admin only)
 */
router.post('/anonymize/:userId', authenticate, authorizeRole(['admin']), async (req, res) => {
  try {
    const { userId } = req.params;
    
    const result = await gdprService.anonymizeUserData(userId);
    
    // Log data anonymization
    auditService.logDataEvent('anonymize_user_data', {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId,
      anonymizationResult: result
    }, req.user);
    
    return res.status(200).json(result);
  } catch (error) {
    logger.error(`Error anonymizing user data: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to anonymize user data' });
  }
});

/**
 * @route GET /api/security/processing-records/:userId
 * @desc Get data processing records for a user
 * @access Private (Admin or own user)
 */
router.get('/processing-records/:userId', authenticate, async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Check if user is authorized to view these records
    if (req.user.role !== 'admin' && req.user.id !== userId) {
      return res.status(403).json({ error: 'Unauthorized to view these records' });
    }
    
    const records = await gdprService.getDataProcessingRecords(userId);
    
    // Log access to processing records
    auditService.logAccessEvent('view_processing_records', {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId
    }, req.user);
    
    return res.status(200).json({
      count: records.length,
      records
    });
  } catch (error) {
    logger.error(`Error getting data processing records: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to get data processing records' });
  }
});

module.exports = router;
