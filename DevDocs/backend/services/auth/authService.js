/**
 * Authentication Service
 * 
 * Provides authentication and authorization functionality.
 */

const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const crypto = require('crypto');
const logger = require('../../utils/logger');

// Secret key for JWT
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const JWT_EXPIRATION = process.env.JWT_EXPIRATION || '24h';
const REFRESH_TOKEN_EXPIRATION = process.env.REFRESH_TOKEN_EXPIRATION || '7d';

// Mock user database (in a real implementation, this would be a database)
const users = [
  {
    id: '1',
    username: 'admin',
    password: '$2b$10$X7o4.KK4XLYFEwmo1vX5eeHzlVtS22vNm/Rj7JaG0B/4vRv3UNpTW', // hashed 'admin123'
    email: 'admin@example.com',
    role: 'admin',
    permissions: ['read', 'write', 'delete', 'admin'],
    refreshTokens: []
  },
  {
    id: '2',
    username: 'user',
    password: '$2b$10$5dwsS5snIRlKu8LKmB5kUOFCLK1VpZkVu.zXRqVJy1rWlPXD6bJWO', // hashed 'user123'
    email: 'user@example.com',
    role: 'user',
    permissions: ['read', 'write'],
    refreshTokens: []
  }
];

/**
 * Authenticate a user
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise<Object>} - Authentication result
 */
async function authenticate(username, password) {
  try {
    // Find user
    const user = users.find(u => u.username === username);
    
    if (!user) {
      logger.warn(`Authentication failed: User ${username} not found`);
      return { success: false, message: 'Invalid username or password' };
    }
    
    // Compare password
    const passwordMatch = await bcrypt.compare(password, user.password);
    
    if (!passwordMatch) {
      logger.warn(`Authentication failed: Invalid password for user ${username}`);
      return { success: false, message: 'Invalid username or password' };
    }
    
    // Generate tokens
    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);
    
    // Store refresh token
    user.refreshTokens.push(refreshToken);
    
    logger.info(`User ${username} authenticated successfully`);
    
    return {
      success: true,
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role
      },
      accessToken,
      refreshToken
    };
  } catch (error) {
    logger.error(`Authentication error: ${error.message}`, error);
    return { success: false, message: 'Authentication failed' };
  }
}

/**
 * Generate an access token
 * @param {Object} user - User object
 * @returns {string} - JWT access token
 */
function generateAccessToken(user) {
  return jwt.sign(
    {
      id: user.id,
      username: user.username,
      role: user.role,
      permissions: user.permissions
    },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRATION }
  );
}

/**
 * Generate a refresh token
 * @param {Object} user - User object
 * @returns {string} - JWT refresh token
 */
function generateRefreshToken(user) {
  const tokenId = crypto.randomBytes(16).toString('hex');
  
  return jwt.sign(
    {
      id: user.id,
      tokenId
    },
    JWT_SECRET,
    { expiresIn: REFRESH_TOKEN_EXPIRATION }
  );
}

/**
 * Refresh an access token
 * @param {string} refreshToken - Refresh token
 * @returns {Promise<Object>} - Refresh result
 */
async function refreshAccessToken(refreshToken) {
  try {
    // Verify refresh token
    const decoded = jwt.verify(refreshToken, JWT_SECRET);
    
    // Find user
    const user = users.find(u => u.id === decoded.id);
    
    if (!user) {
      logger.warn(`Token refresh failed: User not found for token ID ${decoded.id}`);
      return { success: false, message: 'Invalid refresh token' };
    }
    
    // Check if refresh token exists
    if (!user.refreshTokens.includes(refreshToken)) {
      logger.warn(`Token refresh failed: Refresh token not found for user ${user.username}`);
      return { success: false, message: 'Invalid refresh token' };
    }
    
    // Generate new access token
    const accessToken = generateAccessToken(user);
    
    logger.info(`Access token refreshed for user ${user.username}`);
    
    return {
      success: true,
      accessToken
    };
  } catch (error) {
    logger.error(`Token refresh error: ${error.message}`, error);
    return { success: false, message: 'Token refresh failed' };
  }
}

/**
 * Logout a user
 * @param {string} refreshToken - Refresh token
 * @returns {Promise<Object>} - Logout result
 */
async function logout(refreshToken) {
  try {
    // Verify refresh token
    const decoded = jwt.verify(refreshToken, JWT_SECRET);
    
    // Find user
    const user = users.find(u => u.id === decoded.id);
    
    if (!user) {
      logger.warn(`Logout failed: User not found for token ID ${decoded.id}`);
      return { success: false, message: 'Invalid refresh token' };
    }
    
    // Remove refresh token
    user.refreshTokens = user.refreshTokens.filter(token => token !== refreshToken);
    
    logger.info(`User ${user.username} logged out successfully`);
    
    return {
      success: true,
      message: 'Logout successful'
    };
  } catch (error) {
    logger.error(`Logout error: ${error.message}`, error);
    return { success: false, message: 'Logout failed' };
  }
}

/**
 * Verify a JWT token
 * @param {string} token - JWT token
 * @returns {Object} - Verification result
 */
function verifyToken(token) {
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    return { success: true, decoded };
  } catch (error) {
    logger.error(`Token verification error: ${error.message}`, error);
    return { success: false, message: 'Invalid token' };
  }
}

/**
 * Check if a user has a permission
 * @param {Object} user - User object
 * @param {string} permission - Permission to check
 * @returns {boolean} - Whether the user has the permission
 */
function hasPermission(user, permission) {
  return user.permissions.includes(permission) || user.permissions.includes('admin');
}

/**
 * Register a new user
 * @param {Object} userData - User data
 * @returns {Promise<Object>} - Registration result
 */
async function registerUser(userData) {
  try {
    // Check if username already exists
    if (users.some(u => u.username === userData.username)) {
      logger.warn(`Registration failed: Username ${userData.username} already exists`);
      return { success: false, message: 'Username already exists' };
    }
    
    // Check if email already exists
    if (users.some(u => u.email === userData.email)) {
      logger.warn(`Registration failed: Email ${userData.email} already exists`);
      return { success: false, message: 'Email already exists' };
    }
    
    // Hash password
    const hashedPassword = await bcrypt.hash(userData.password, 10);
    
    // Create new user
    const newUser = {
      id: (users.length + 1).toString(),
      username: userData.username,
      password: hashedPassword,
      email: userData.email,
      role: 'user',
      permissions: ['read', 'write'],
      refreshTokens: []
    };
    
    // Add user to database
    users.push(newUser);
    
    logger.info(`User ${userData.username} registered successfully`);
    
    return {
      success: true,
      user: {
        id: newUser.id,
        username: newUser.username,
        email: newUser.email,
        role: newUser.role
      }
    };
  } catch (error) {
    logger.error(`Registration error: ${error.message}`, error);
    return { success: false, message: 'Registration failed' };
  }
}

/**
 * Change user password
 * @param {string} userId - User ID
 * @param {string} currentPassword - Current password
 * @param {string} newPassword - New password
 * @returns {Promise<Object>} - Password change result
 */
async function changePassword(userId, currentPassword, newPassword) {
  try {
    // Find user
    const user = users.find(u => u.id === userId);
    
    if (!user) {
      logger.warn(`Password change failed: User with ID ${userId} not found`);
      return { success: false, message: 'User not found' };
    }
    
    // Compare current password
    const passwordMatch = await bcrypt.compare(currentPassword, user.password);
    
    if (!passwordMatch) {
      logger.warn(`Password change failed: Invalid current password for user ${user.username}`);
      return { success: false, message: 'Invalid current password' };
    }
    
    // Hash new password
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    
    // Update password
    user.password = hashedPassword;
    
    // Invalidate all refresh tokens
    user.refreshTokens = [];
    
    logger.info(`Password changed for user ${user.username}`);
    
    return {
      success: true,
      message: 'Password changed successfully'
    };
  } catch (error) {
    logger.error(`Password change error: ${error.message}`, error);
    return { success: false, message: 'Password change failed' };
  }
}

module.exports = {
  authenticate,
  refreshAccessToken,
  logout,
  verifyToken,
  hasPermission,
  registerUser,
  changePassword
};
