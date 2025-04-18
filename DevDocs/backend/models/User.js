/**
 * User Model
 * 
 * Represents a user in the system.
 * Provides methods for user management.
 */

const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const supabase = require('../db/supabase');
const logger = require('../utils/logger');
const config = require('../config');
const { BadRequestError, NotFoundError, ConflictError } = require('../middleware/errorMiddleware');

/**
 * User class
 */
class User {
  /**
   * Create a new user
   * @param {Object} userData - User data
   * @returns {Promise<Object>} Created user
   */
  static async create(userData) {
    try {
      const { email, password, firstName, lastName, role = 'user' } = userData;
      
      // Validate required fields
      if (!email || !password) {
        throw new BadRequestError('Email and password are required');
      }
      
      // Check if user already exists
      const client = supabase.getClient();
      const { data: existingUser, error: checkError } = await client
        .from('users')
        .select('id')
        .eq('email', email.toLowerCase())
        .maybeSingle();
      
      if (checkError) {
        logger.error('Error checking existing user:', checkError);
        throw new Error('Error checking existing user');
      }
      
      if (existingUser) {
        throw new ConflictError('User with this email already exists');
      }
      
      // Hash password
      const passwordHash = await bcrypt.hash(password, config.auth.saltRounds);
      
      // Create user
      const { data: newUser, error } = await client
        .from('users')
        .insert({
          id: uuidv4(),
          email: email.toLowerCase(),
          password_hash: passwordHash,
          first_name: firstName,
          last_name: lastName,
          role,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select('id, email, first_name, last_name, role, created_at')
        .single();
      
      if (error) {
        logger.error('Error creating user:', error);
        throw new Error('Error creating user');
      }
      
      return {
        id: newUser.id,
        email: newUser.email,
        firstName: newUser.first_name,
        lastName: newUser.last_name,
        role: newUser.role,
        createdAt: newUser.created_at
      };
    } catch (error) {
      logger.error('Error in User.create:', error);
      throw error;
    }
  }
  
  /**
   * Find a user by ID
   * @param {string} id - User ID
   * @returns {Promise<Object>} User
   */
  static async findById(id) {
    try {
      const client = supabase.getClient();
      const { data: user, error } = await client
        .from('users')
        .select('id, email, first_name, last_name, role, created_at, updated_at, last_login, is_active, preferences')
        .eq('id', id)
        .single();
      
      if (error) {
        logger.error('Error finding user by ID:', error);
        throw new Error('Error finding user');
      }
      
      if (!user) {
        throw new NotFoundError('User not found');
      }
      
      return {
        id: user.id,
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name,
        role: user.role,
        createdAt: user.created_at,
        updatedAt: user.updated_at,
        lastLogin: user.last_login,
        isActive: user.is_active,
        preferences: user.preferences
      };
    } catch (error) {
      logger.error('Error in User.findById:', error);
      throw error;
    }
  }
  
  /**
   * Find a user by email
   * @param {string} email - User email
   * @returns {Promise<Object>} User
   */
  static async findByEmail(email) {
    try {
      const client = supabase.getClient();
      const { data: user, error } = await client
        .from('users')
        .select('id, email, first_name, last_name, role, created_at, updated_at, last_login, is_active, preferences')
        .eq('email', email.toLowerCase())
        .single();
      
      if (error) {
        logger.error('Error finding user by email:', error);
        throw new Error('Error finding user');
      }
      
      if (!user) {
        throw new NotFoundError('User not found');
      }
      
      return {
        id: user.id,
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name,
        role: user.role,
        createdAt: user.created_at,
        updatedAt: user.updated_at,
        lastLogin: user.last_login,
        isActive: user.is_active,
        preferences: user.preferences
      };
    } catch (error) {
      logger.error('Error in User.findByEmail:', error);
      throw error;
    }
  }
  
  /**
   * Update a user
   * @param {string} id - User ID
   * @param {Object} userData - User data to update
   * @returns {Promise<Object>} Updated user
   */
  static async update(id, userData) {
    try {
      const { email, firstName, lastName, role, isActive, preferences } = userData;
      
      // Prepare update data
      const updateData = {};
      
      if (email) updateData.email = email.toLowerCase();
      if (firstName !== undefined) updateData.first_name = firstName;
      if (lastName !== undefined) updateData.last_name = lastName;
      if (role) updateData.role = role;
      if (isActive !== undefined) updateData.is_active = isActive;
      if (preferences) updateData.preferences = preferences;
      
      updateData.updated_at = new Date().toISOString();
      
      // Update user
      const client = supabase.getClient();
      const { data: updatedUser, error } = await client
        .from('users')
        .update(updateData)
        .eq('id', id)
        .select('id, email, first_name, last_name, role, created_at, updated_at, last_login, is_active, preferences')
        .single();
      
      if (error) {
        logger.error('Error updating user:', error);
        throw new Error('Error updating user');
      }
      
      if (!updatedUser) {
        throw new NotFoundError('User not found');
      }
      
      return {
        id: updatedUser.id,
        email: updatedUser.email,
        firstName: updatedUser.first_name,
        lastName: updatedUser.last_name,
        role: updatedUser.role,
        createdAt: updatedUser.created_at,
        updatedAt: updatedUser.updated_at,
        lastLogin: updatedUser.last_login,
        isActive: updatedUser.is_active,
        preferences: updatedUser.preferences
      };
    } catch (error) {
      logger.error('Error in User.update:', error);
      throw error;
    }
  }
  
  /**
   * Change user password
   * @param {string} id - User ID
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @returns {Promise<boolean>} True if password was changed
   */
  static async changePassword(id, currentPassword, newPassword) {
    try {
      // Get user with password hash
      const client = supabase.getClient();
      const { data: user, error } = await client
        .from('users')
        .select('password_hash')
        .eq('id', id)
        .single();
      
      if (error) {
        logger.error('Error getting user for password change:', error);
        throw new Error('Error changing password');
      }
      
      if (!user) {
        throw new NotFoundError('User not found');
      }
      
      // Verify current password
      const isPasswordValid = await bcrypt.compare(currentPassword, user.password_hash);
      
      if (!isPasswordValid) {
        throw new BadRequestError('Current password is incorrect');
      }
      
      // Hash new password
      const passwordHash = await bcrypt.hash(newPassword, config.auth.saltRounds);
      
      // Update password
      const { error: updateError } = await client
        .from('users')
        .update({
          password_hash: passwordHash,
          updated_at: new Date().toISOString()
        })
        .eq('id', id);
      
      if (updateError) {
        logger.error('Error updating password:', updateError);
        throw new Error('Error changing password');
      }
      
      return true;
    } catch (error) {
      logger.error('Error in User.changePassword:', error);
      throw error;
    }
  }
  
  /**
   * Delete a user
   * @param {string} id - User ID
   * @returns {Promise<boolean>} True if user was deleted
   */
  static async delete(id) {
    try {
      const client = supabase.getClient();
      const { error } = await client
        .from('users')
        .delete()
        .eq('id', id);
      
      if (error) {
        logger.error('Error deleting user:', error);
        throw new Error('Error deleting user');
      }
      
      return true;
    } catch (error) {
      logger.error('Error in User.delete:', error);
      throw error;
    }
  }
  
  /**
   * Authenticate a user
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} Authentication result with user and token
   */
  static async authenticate(email, password) {
    try {
      // Validate required fields
      if (!email || !password) {
        throw new BadRequestError('Email and password are required');
      }
      
      // Get user with password hash
      const client = supabase.getClient();
      const { data: user, error } = await client
        .from('users')
        .select('id, email, password_hash, first_name, last_name, role, is_active')
        .eq('email', email.toLowerCase())
        .single();
      
      if (error) {
        logger.error('Error authenticating user:', error);
        throw new Error('Error authenticating user');
      }
      
      if (!user) {
        throw new BadRequestError('Invalid email or password');
      }
      
      // Check if user is active
      if (!user.is_active) {
        throw new BadRequestError('User account is inactive');
      }
      
      // Verify password
      const isPasswordValid = await bcrypt.compare(password, user.password_hash);
      
      if (!isPasswordValid) {
        throw new BadRequestError('Invalid email or password');
      }
      
      // Update last login
      await client
        .from('users')
        .update({
          last_login: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .eq('id', user.id);
      
      // Generate JWT token
      const token = jwt.sign(
        {
          id: user.id,
          email: user.email,
          role: user.role
        },
        config.auth.jwtSecret,
        {
          expiresIn: config.auth.jwtExpiresIn
        }
      );
      
      return {
        user: {
          id: user.id,
          email: user.email,
          firstName: user.first_name,
          lastName: user.last_name,
          role: user.role
        },
        token
      };
    } catch (error) {
      logger.error('Error in User.authenticate:', error);
      throw error;
    }
  }
  
  /**
   * Get all users
   * @param {Object} options - Query options
   * @returns {Promise<Object>} Users and count
   */
  static async getAll(options = {}) {
    try {
      const {
        page = 1,
        limit = 10,
        sortBy = 'created_at',
        sortOrder = 'desc',
        search = '',
        role = ''
      } = options;
      
      const offset = (page - 1) * limit;
      
      // Build query
      const client = supabase.getClient();
      let query = client
        .from('users')
        .select('id, email, first_name, last_name, role, created_at, updated_at, last_login, is_active', { count: 'exact' });
      
      // Apply filters
      if (search) {
        query = query.or(`email.ilike.%${search}%,first_name.ilike.%${search}%,last_name.ilike.%${search}%`);
      }
      
      if (role) {
        query = query.eq('role', role);
      }
      
      // Apply sorting and pagination
      query = query
        .order(sortBy, { ascending: sortOrder === 'asc' })
        .range(offset, offset + limit - 1);
      
      // Execute query
      const { data: users, error, count } = await query;
      
      if (error) {
        logger.error('Error getting users:', error);
        throw new Error('Error getting users');
      }
      
      return {
        users: users.map(user => ({
          id: user.id,
          email: user.email,
          firstName: user.first_name,
          lastName: user.last_name,
          role: user.role,
          createdAt: user.created_at,
          updatedAt: user.updated_at,
          lastLogin: user.last_login,
          isActive: user.is_active
        })),
        count,
        page,
        limit,
        totalPages: Math.ceil(count / limit)
      };
    } catch (error) {
      logger.error('Error in User.getAll:', error);
      throw error;
    }
  }
}

module.exports = User;
