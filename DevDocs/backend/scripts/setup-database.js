#!/usr/bin/env node

/**
 * Database Setup Script
 * 
 * This script sets up the database by running all migrations.
 * It also creates a default admin user if one doesn't exist.
 */

require('dotenv').config();
const migrationRunner = require('../db/migrationRunner');
const User = require('../models/User');
const logger = require('../utils/logger');
const supabase = require('../db/supabase');

async function main() {
  try {
    logger.info('Starting database setup');
    
    // Run migrations
    logger.info('Running migrations');
    await migrationRunner.runMigrations();
    
    // Check if admin user exists
    logger.info('Checking for admin user');
    
    const client = supabase.getClient();
    const { data: adminUser, error } = await client
      .from('users')
      .select('id')
      .eq('role', 'admin')
      .maybeSingle();
    
    if (error) {
      logger.error('Error checking for admin user:', error);
      throw error;
    }
    
    // Create admin user if none exists
    if (!adminUser) {
      logger.info('Creating admin user');
      
      const adminEmail = process.env.ADMIN_EMAIL || 'admin@findoc-analyzer.com';
      const adminPassword = process.env.ADMIN_PASSWORD || 'admin123';
      
      await User.create({
        email: adminEmail,
        password: adminPassword,
        firstName: 'Admin',
        lastName: 'User',
        role: 'admin'
      });
      
      logger.info(`Admin user created with email: ${adminEmail}`);
      logger.warn('Please change the admin password immediately!');
    } else {
      logger.info('Admin user already exists');
    }
    
    // Create default organization if none exists
    logger.info('Checking for default organization');
    
    const { data: defaultOrg, error: orgError } = await client
      .from('organizations')
      .select('id')
      .eq('name', 'Default Organization')
      .maybeSingle();
    
    if (orgError) {
      logger.error('Error checking for default organization:', orgError);
      throw orgError;
    }
    
    if (!defaultOrg) {
      logger.info('Creating default organization');
      
      const { data: newOrg, error: createOrgError } = await client
        .from('organizations')
        .insert({
          name: 'Default Organization',
          description: 'Default organization created during setup',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select('id')
        .single();
      
      if (createOrgError) {
        logger.error('Error creating default organization:', createOrgError);
        throw createOrgError;
      }
      
      logger.info(`Default organization created with ID: ${newOrg.id}`);
      
      // Add admin user to default organization
      if (!adminUser) {
        // Get the admin user we just created
        const { data: newAdmin, error: adminError } = await client
          .from('users')
          .select('id')
          .eq('role', 'admin')
          .single();
        
        if (adminError) {
          logger.error('Error getting admin user:', adminError);
          throw adminError;
        }
        
        // Add admin to organization
        const { error: memberError } = await client
          .from('organization_users')
          .insert({
            organization_id: newOrg.id,
            user_id: newAdmin.id,
            role: 'admin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          });
        
        if (memberError) {
          logger.error('Error adding admin to organization:', memberError);
          throw memberError;
        }
        
        logger.info(`Admin user added to default organization`);
      } else {
        // Add existing admin to organization
        const { error: memberError } = await client
          .from('organization_users')
          .insert({
            organization_id: newOrg.id,
            user_id: adminUser.id,
            role: 'admin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          });
        
        if (memberError) {
          logger.error('Error adding admin to organization:', memberError);
          throw memberError;
        }
        
        logger.info(`Admin user added to default organization`);
      }
    } else {
      logger.info('Default organization already exists');
    }
    
    logger.info('Database setup completed successfully');
    process.exit(0);
  } catch (error) {
    logger.error('Database setup failed:', error);
    process.exit(1);
  }
}

// Run the script
main();
