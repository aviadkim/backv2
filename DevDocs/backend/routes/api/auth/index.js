/**
 * Authentication Routes
 * 
 * API routes for authentication and user management.
 */

const express = require('express');
const router = express.Router();
const authService = require('../../../services/auth/authService');
const { authenticate } = require('../../../middleware/authMiddleware');
const logger = require('../../../utils/logger');

/**
 * @route POST /api/auth/login
 * @desc Authenticate a user and get tokens
 * @access Public
 */
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }
    
    const result = await authService.authenticate(username, password);
    
    if (!result.success) {
      return res.status(401).json({ error: result.message });
    }
    
    // Set refresh token as HTTP-only cookie
    res.cookie('refreshToken', result.refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
    });
    
    return res.status(200).json({
      user: result.user,
      accessToken: result.accessToken
    });
  } catch (error) {
    logger.error(`Login error: ${error.message}`, error);
    return res.status(500).json({ error: 'Login failed' });
  }
});

/**
 * @route POST /api/auth/refresh
 * @desc Refresh access token
 * @access Public
 */
router.post('/refresh', async (req, res) => {
  try {
    const refreshToken = req.cookies.refreshToken;
    
    if (!refreshToken) {
      return res.status(400).json({ error: 'Refresh token is required' });
    }
    
    const result = await authService.refreshAccessToken(refreshToken);
    
    if (!result.success) {
      return res.status(401).json({ error: result.message });
    }
    
    return res.status(200).json({
      accessToken: result.accessToken
    });
  } catch (error) {
    logger.error(`Token refresh error: ${error.message}`, error);
    return res.status(500).json({ error: 'Token refresh failed' });
  }
});

/**
 * @route POST /api/auth/logout
 * @desc Logout a user
 * @access Public
 */
router.post('/logout', async (req, res) => {
  try {
    const refreshToken = req.cookies.refreshToken;
    
    if (!refreshToken) {
      return res.status(400).json({ error: 'Refresh token is required' });
    }
    
    const result = await authService.logout(refreshToken);
    
    // Clear refresh token cookie
    res.clearCookie('refreshToken');
    
    return res.status(200).json({ message: 'Logout successful' });
  } catch (error) {
    logger.error(`Logout error: ${error.message}`, error);
    return res.status(500).json({ error: 'Logout failed' });
  }
});

/**
 * @route POST /api/auth/register
 * @desc Register a new user
 * @access Public
 */
router.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password are required' });
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ error: 'Invalid email format' });
    }
    
    // Validate password strength
    if (password.length < 8) {
      return res.status(400).json({ error: 'Password must be at least 8 characters long' });
    }
    
    const result = await authService.registerUser({ username, email, password });
    
    if (!result.success) {
      return res.status(400).json({ error: result.message });
    }
    
    return res.status(201).json({
      message: 'User registered successfully',
      user: result.user
    });
  } catch (error) {
    logger.error(`Registration error: ${error.message}`, error);
    return res.status(500).json({ error: 'Registration failed' });
  }
});

/**
 * @route POST /api/auth/change-password
 * @desc Change user password
 * @access Private
 */
router.post('/change-password', authenticate, async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;
    
    if (!currentPassword || !newPassword) {
      return res.status(400).json({ error: 'Current password and new password are required' });
    }
    
    // Validate password strength
    if (newPassword.length < 8) {
      return res.status(400).json({ error: 'New password must be at least 8 characters long' });
    }
    
    const result = await authService.changePassword(req.user.id, currentPassword, newPassword);
    
    if (!result.success) {
      return res.status(400).json({ error: result.message });
    }
    
    // Clear refresh token cookie
    res.clearCookie('refreshToken');
    
    return res.status(200).json({ message: 'Password changed successfully' });
  } catch (error) {
    logger.error(`Password change error: ${error.message}`, error);
    return res.status(500).json({ error: 'Password change failed' });
  }
});

/**
 * @route GET /api/auth/me
 * @desc Get current user information
 * @access Private
 */
router.get('/me', authenticate, (req, res) => {
  try {
    return res.status(200).json({
      user: {
        id: req.user.id,
        username: req.user.username,
        role: req.user.role,
        permissions: req.user.permissions
      }
    });
  } catch (error) {
    logger.error(`Get user error: ${error.message}`, error);
    return res.status(500).json({ error: 'Failed to get user information' });
  }
});

module.exports = router;
