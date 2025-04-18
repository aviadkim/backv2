/**
 * Authentication Controller
 * 
 * Handles user authentication and authorization.
 */

const User = require('../models/User');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorMiddleware');
const { BadRequestError } = require('../middleware/errorMiddleware');

/**
 * Register a new user
 * @route POST /api/auth/register
 * @access Public
 */
const register = asyncHandler(async (req, res) => {
  const { email, password, firstName, lastName } = req.body;
  
  // Create user
  const user = await User.create({
    email,
    password,
    firstName,
    lastName,
    role: 'user'
  });
  
  // Log registration
  logger.info(`User registered: ${user.id}`);
  
  res.status(201).json({
    status: 'success',
    data: {
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role
      }
    }
  });
});

/**
 * Login user
 * @route POST /api/auth/login
 * @access Public
 */
const login = asyncHandler(async (req, res) => {
  const { email, password } = req.body;
  
  // Authenticate user
  const { user, token } = await User.authenticate(email, password);
  
  // Set token in cookie
  res.cookie('token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 24 * 60 * 60 * 1000 // 1 day
  });
  
  // Log login
  logger.info(`User logged in: ${user.id}`);
  
  res.json({
    status: 'success',
    data: {
      user,
      token
    }
  });
});

/**
 * Logout user
 * @route POST /api/auth/logout
 * @access Private
 */
const logout = asyncHandler(async (req, res) => {
  // Clear token cookie
  res.clearCookie('token');
  
  // Log logout
  if (req.user) {
    logger.info(`User logged out: ${req.user.id}`);
  }
  
  res.json({
    status: 'success',
    message: 'Logged out successfully'
  });
});

/**
 * Get current user
 * @route GET /api/auth/me
 * @access Private
 */
const getCurrentUser = asyncHandler(async (req, res) => {
  const user = await User.findById(req.user.id);
  
  res.json({
    status: 'success',
    data: {
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        preferences: user.preferences
      }
    }
  });
});

/**
 * Update user profile
 * @route PUT /api/auth/profile
 * @access Private
 */
const updateProfile = asyncHandler(async (req, res) => {
  const { firstName, lastName, preferences } = req.body;
  
  // Update user
  const user = await User.update(req.user.id, {
    firstName,
    lastName,
    preferences
  });
  
  // Log profile update
  logger.info(`User profile updated: ${user.id}`);
  
  res.json({
    status: 'success',
    data: {
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        preferences: user.preferences
      }
    }
  });
});

/**
 * Change password
 * @route PUT /api/auth/change-password
 * @access Private
 */
const changePassword = asyncHandler(async (req, res) => {
  const { currentPassword, newPassword } = req.body;
  
  // Validate passwords
  if (!currentPassword || !newPassword) {
    throw new BadRequestError('Current password and new password are required');
  }
  
  if (newPassword.length < 8) {
    throw new BadRequestError('New password must be at least 8 characters long');
  }
  
  // Change password
  await User.changePassword(req.user.id, currentPassword, newPassword);
  
  // Log password change
  logger.info(`User password changed: ${req.user.id}`);
  
  res.json({
    status: 'success',
    message: 'Password changed successfully'
  });
});

/**
 * Request password reset
 * @route POST /api/auth/forgot-password
 * @access Public
 */
const forgotPassword = asyncHandler(async (req, res) => {
  const { email } = req.body;
  
  if (!email) {
    throw new BadRequestError('Email is required');
  }
  
  // TODO: Implement password reset functionality
  // This would typically involve:
  // 1. Generate a reset token
  // 2. Store the token in the database with an expiration
  // 3. Send an email with a reset link
  
  // For now, just log the request
  logger.info(`Password reset requested for email: ${email}`);
  
  res.json({
    status: 'success',
    message: 'If an account with that email exists, a password reset link has been sent'
  });
});

/**
 * Reset password
 * @route POST /api/auth/reset-password
 * @access Public
 */
const resetPassword = asyncHandler(async (req, res) => {
  const { token, newPassword } = req.body;
  
  if (!token || !newPassword) {
    throw new BadRequestError('Token and new password are required');
  }
  
  if (newPassword.length < 8) {
    throw new BadRequestError('New password must be at least 8 characters long');
  }
  
  // TODO: Implement password reset functionality
  // This would typically involve:
  // 1. Verify the reset token
  // 2. Update the user's password
  // 3. Invalidate the token
  
  // For now, just log the request
  logger.info('Password reset attempted');
  
  res.json({
    status: 'success',
    message: 'Password has been reset successfully'
  });
});

module.exports = {
  register,
  login,
  logout,
  getCurrentUser,
  updateProfile,
  changePassword,
  forgotPassword,
  resetPassword
};
