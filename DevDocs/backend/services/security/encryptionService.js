/**
 * Encryption Service
 * 
 * Provides encryption and decryption functionality for sensitive data.
 */

const crypto = require('crypto');
const logger = require('../../utils/logger');

// Encryption settings
const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32; // 256 bits
const IV_LENGTH = 16; // 128 bits
const AUTH_TAG_LENGTH = 16; // 128 bits

// Encryption key (in a real implementation, this would be stored securely)
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || crypto.randomBytes(KEY_LENGTH).toString('hex');

/**
 * Encrypt data
 * @param {string|Object} data - Data to encrypt
 * @returns {Object} - Encrypted data
 */
function encrypt(data) {
  try {
    // Convert data to string if it's an object
    const dataString = typeof data === 'object' ? JSON.stringify(data) : data.toString();
    
    // Generate random initialization vector
    const iv = crypto.randomBytes(IV_LENGTH);
    
    // Create cipher
    const cipher = crypto.createCipheriv(ALGORITHM, Buffer.from(ENCRYPTION_KEY, 'hex'), iv);
    
    // Encrypt data
    let encrypted = cipher.update(dataString, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    // Get authentication tag
    const authTag = cipher.getAuthTag();
    
    // Return encrypted data with IV and auth tag
    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  } catch (error) {
    logger.error(`Encryption error: ${error.message}`, error);
    throw new Error('Encryption failed');
  }
}

/**
 * Decrypt data
 * @param {Object} encryptedData - Encrypted data object
 * @returns {string|Object} - Decrypted data
 */
function decrypt(encryptedData) {
  try {
    // Extract encrypted data, IV, and auth tag
    const { encrypted, iv, authTag } = encryptedData;
    
    // Create decipher
    const decipher = crypto.createDecipheriv(
      ALGORITHM,
      Buffer.from(ENCRYPTION_KEY, 'hex'),
      Buffer.from(iv, 'hex')
    );
    
    // Set authentication tag
    decipher.setAuthTag(Buffer.from(authTag, 'hex'));
    
    // Decrypt data
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    // Try to parse as JSON if possible
    try {
      return JSON.parse(decrypted);
    } catch {
      return decrypted;
    }
  } catch (error) {
    logger.error(`Decryption error: ${error.message}`, error);
    throw new Error('Decryption failed');
  }
}

/**
 * Hash data (one-way)
 * @param {string} data - Data to hash
 * @param {string} salt - Salt for hashing (optional)
 * @returns {Object} - Hashed data
 */
function hash(data, salt = null) {
  try {
    // Generate salt if not provided
    const useSalt = salt || crypto.randomBytes(16).toString('hex');
    
    // Hash data
    const hashedData = crypto.pbkdf2Sync(
      data.toString(),
      useSalt,
      10000, // Iterations
      64, // Key length
      'sha512'
    ).toString('hex');
    
    return {
      hash: hashedData,
      salt: useSalt
    };
  } catch (error) {
    logger.error(`Hashing error: ${error.message}`, error);
    throw new Error('Hashing failed');
  }
}

/**
 * Verify hashed data
 * @param {string} data - Data to verify
 * @param {string} hashedData - Hashed data
 * @param {string} salt - Salt used for hashing
 * @returns {boolean} - Whether the data matches the hash
 */
function verifyHash(data, hashedData, salt) {
  try {
    // Hash the data with the provided salt
    const { hash: newHash } = hash(data, salt);
    
    // Compare hashes
    return newHash === hashedData;
  } catch (error) {
    logger.error(`Hash verification error: ${error.message}`, error);
    throw new Error('Hash verification failed');
  }
}

/**
 * Generate a secure random token
 * @param {number} length - Token length in bytes
 * @returns {string} - Random token
 */
function generateToken(length = 32) {
  try {
    return crypto.randomBytes(length).toString('hex');
  } catch (error) {
    logger.error(`Token generation error: ${error.message}`, error);
    throw new Error('Token generation failed');
  }
}

module.exports = {
  encrypt,
  decrypt,
  hash,
  verifyHash,
  generateToken
};
