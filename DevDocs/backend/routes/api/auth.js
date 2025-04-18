/**
 * Authentication Routes
 * 
 * Handles user authentication and authorization routes.
 */

const express = require('express');
const router = express.Router();
const authController = require('../../controllers/authController');
const { verifyToken } = require('../../middleware/authMiddleware');

/**
 * @route POST /api/auth/register
 * @description Register a new user
 * @access Public
 */
router.post('/register', authController.register);

/**
 * @route POST /api/auth/login
 * @description Login user
 * @access Public
 */
router.post('/login', authController.login);

/**
 * @route POST /api/auth/logout
 * @description Logout user
 * @access Private
 */
router.post('/logout', verifyToken, authController.logout);

/**
 * @route GET /api/auth/me
 * @description Get current user
 * @access Private
 */
router.get('/me', verifyToken, authController.getCurrentUser);

/**
 * @route PUT /api/auth/profile
 * @description Update user profile
 * @access Private
 */
router.put('/profile', verifyToken, authController.updateProfile);

/**
 * @route PUT /api/auth/change-password
 * @description Change password
 * @access Private
 */
router.put('/change-password', verifyToken, authController.changePassword);

/**
 * @route POST /api/auth/forgot-password
 * @description Request password reset
 * @access Public
 */
router.post('/forgot-password', authController.forgotPassword);

/**
 * @route POST /api/auth/reset-password
 * @description Reset password
 * @access Public
 */
router.post('/reset-password', authController.resetPassword);

module.exports = router;
