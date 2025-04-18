#!/usr/bin/env node

/**
 * Database Migration Runner Script
 * 
 * This script runs database migrations.
 * It can be used to apply all pending migrations or a specific migration.
 */

require('dotenv').config();
const migrationRunner = require('../db/migrationRunner');
const logger = require('../utils/logger');

// Parse command line arguments
const args = process.argv.slice(2);
const command = args[0];
const migrationName = args[1];

async function main() {
  try {
    logger.info('Starting database migration runner');
    
    switch (command) {
      case 'run':
        logger.info('Running all pending migrations');
        await migrationRunner.runMigrations();
        break;
        
      case 'apply':
        if (!migrationName) {
          logger.error('Migration name is required for apply command');
          process.exit(1);
        }
        
        logger.info(`Applying migration: ${migrationName}`);
        await migrationRunner.applySpecificMigration(migrationName);
        break;
        
      case 'rollback':
        logger.info('Rolling back last migration');
        await migrationRunner.rollbackLastMigration();
        break;
        
      case 'list':
        logger.info('Listing migrations');
        const appliedMigrations = await migrationRunner.getAppliedMigrations();
        const pendingMigrations = await migrationRunner.getPendingMigrations(appliedMigrations);
        
        logger.info('Applied migrations:');
        appliedMigrations.forEach(migration => logger.info(`- ${migration}`));
        
        logger.info('Pending migrations:');
        pendingMigrations.forEach(migration => logger.info(`- ${migration}`));
        break;
        
      default:
        logger.error(`Unknown command: ${command}`);
        logger.info('Available commands:');
        logger.info('- run: Run all pending migrations');
        logger.info('- apply <migration-name>: Apply a specific migration');
        logger.info('- rollback: Rollback the last applied migration');
        logger.info('- list: List applied and pending migrations');
        process.exit(1);
    }
    
    logger.info('Migration runner completed successfully');
    process.exit(0);
  } catch (error) {
    logger.error('Migration runner failed:', error);
    process.exit(1);
  }
}

// Run the script
main();
