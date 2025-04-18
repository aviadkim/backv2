/**
 * Database Migration Runner
 * 
 * Runs database migrations in order based on their filenames.
 * Tracks applied migrations in a migrations table.
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readdir = promisify(fs.readdir);
const readFile = promisify(fs.readFile);
const supabase = require('./supabase');
const logger = require('../utils/logger');
const { BadRequestError } = require('../middleware/errorMiddleware');

// Migrations directory
const MIGRATIONS_DIR = path.join(__dirname, 'migrations');

/**
 * Create migrations table if it doesn't exist
 * @returns {Promise<void>}
 */
async function createMigrationsTable() {
  try {
    const client = supabase.getClient();
    
    // Check if migrations table exists
    const { data: tableExists, error: tableCheckError } = await client.rpc(
      'check_table_exists',
      { table_name: 'migrations' }
    );
    
    if (tableCheckError) {
      // Create function to check if table exists
      await client.rpc('create_check_table_exists_function', {}, {
        headers: {
          'Content-Type': 'application/json',
          'Prefer': 'return=minimal'
        }
      });
      
      // Check again
      const { data: tableExistsRetry, error: tableCheckErrorRetry } = await client.rpc(
        'check_table_exists',
        { table_name: 'migrations' }
      );
      
      if (tableCheckErrorRetry) {
        throw new Error(`Failed to check if migrations table exists: ${tableCheckErrorRetry.message}`);
      }
      
      if (!tableExistsRetry) {
        // Create migrations table
        await client.rpc('create_migrations_table', {}, {
          headers: {
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
          }
        });
      }
    } else if (!tableExists) {
      // Create migrations table
      await client.rpc('create_migrations_table', {}, {
        headers: {
          'Content-Type': 'application/json',
          'Prefer': 'return=minimal'
        }
      });
    }
    
    logger.info('Migrations table ready');
  } catch (error) {
    logger.error('Failed to create migrations table:', error);
    throw error;
  }
}

/**
 * Get applied migrations
 * @returns {Promise<string[]>} Array of applied migration names
 */
async function getAppliedMigrations() {
  try {
    const client = supabase.getClient();
    
    const { data, error } = await client
      .from('migrations')
      .select('name')
      .order('applied_at', { ascending: true });
    
    if (error) {
      throw new Error(`Failed to get applied migrations: ${error.message}`);
    }
    
    return data.map(migration => migration.name);
  } catch (error) {
    logger.error('Failed to get applied migrations:', error);
    throw error;
  }
}

/**
 * Get pending migrations
 * @param {string[]} appliedMigrations - Array of applied migration names
 * @returns {Promise<string[]>} Array of pending migration filenames
 */
async function getPendingMigrations(appliedMigrations) {
  try {
    // Get all migration files
    const files = await readdir(MIGRATIONS_DIR);
    
    // Filter SQL files and sort by name
    const migrationFiles = files
      .filter(file => file.endsWith('.sql'))
      .sort();
    
    // Filter out applied migrations
    const pendingMigrations = migrationFiles.filter(
      file => !appliedMigrations.includes(file)
    );
    
    return pendingMigrations;
  } catch (error) {
    logger.error('Failed to get pending migrations:', error);
    throw error;
  }
}

/**
 * Apply a migration
 * @param {string} migrationFile - Migration filename
 * @returns {Promise<void>}
 */
async function applyMigration(migrationFile) {
  try {
    const client = supabase.getClient();
    
    // Read migration file
    const filePath = path.join(MIGRATIONS_DIR, migrationFile);
    const sql = await readFile(filePath, 'utf8');
    
    logger.info(`Applying migration: ${migrationFile}`);
    
    // Execute migration
    const { error } = await client.rpc('run_sql', { sql }, {
      headers: {
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      }
    });
    
    if (error) {
      throw new Error(`Failed to apply migration ${migrationFile}: ${error.message}`);
    }
    
    // Record migration
    const { error: insertError } = await client
      .from('migrations')
      .insert({
        name: migrationFile,
        applied_at: new Date().toISOString()
      });
    
    if (insertError) {
      throw new Error(`Failed to record migration ${migrationFile}: ${insertError.message}`);
    }
    
    logger.info(`Migration applied: ${migrationFile}`);
  } catch (error) {
    logger.error(`Failed to apply migration ${migrationFile}:`, error);
    throw error;
  }
}

/**
 * Run all pending migrations
 * @returns {Promise<void>}
 */
async function runMigrations() {
  try {
    // Create migrations table if it doesn't exist
    await createMigrationsTable();
    
    // Get applied migrations
    const appliedMigrations = await getAppliedMigrations();
    logger.info(`Found ${appliedMigrations.length} applied migrations`);
    
    // Get pending migrations
    const pendingMigrations = await getPendingMigrations(appliedMigrations);
    logger.info(`Found ${pendingMigrations.length} pending migrations`);
    
    if (pendingMigrations.length === 0) {
      logger.info('No pending migrations to apply');
      return;
    }
    
    // Apply pending migrations
    for (const migrationFile of pendingMigrations) {
      await applyMigration(migrationFile);
    }
    
    logger.info(`Applied ${pendingMigrations.length} migrations`);
  } catch (error) {
    logger.error('Failed to run migrations:', error);
    throw error;
  }
}

/**
 * Apply a specific migration
 * @param {string} migrationName - Migration name
 * @returns {Promise<void>}
 */
async function applySpecificMigration(migrationName) {
  try {
    // Create migrations table if it doesn't exist
    await createMigrationsTable();
    
    // Get applied migrations
    const appliedMigrations = await getAppliedMigrations();
    
    // Check if migration is already applied
    if (appliedMigrations.includes(migrationName)) {
      throw new BadRequestError(`Migration ${migrationName} is already applied`);
    }
    
    // Check if migration file exists
    const filePath = path.join(MIGRATIONS_DIR, migrationName);
    
    if (!fs.existsSync(filePath)) {
      throw new BadRequestError(`Migration file ${migrationName} not found`);
    }
    
    // Apply migration
    await applyMigration(migrationName);
    
    logger.info(`Applied migration: ${migrationName}`);
  } catch (error) {
    logger.error(`Failed to apply migration ${migrationName}:`, error);
    throw error;
  }
}

/**
 * Rollback the last applied migration
 * @returns {Promise<void>}
 */
async function rollbackLastMigration() {
  try {
    const client = supabase.getClient();
    
    // Get the last applied migration
    const { data, error } = await client
      .from('migrations')
      .select('*')
      .order('applied_at', { ascending: false })
      .limit(1)
      .single();
    
    if (error) {
      throw new Error(`Failed to get last migration: ${error.message}`);
    }
    
    if (!data) {
      logger.info('No migrations to rollback');
      return;
    }
    
    const lastMigration = data;
    
    // Check if rollback file exists
    const migrationName = lastMigration.name;
    const rollbackName = migrationName.replace('.sql', '.rollback.sql');
    const rollbackPath = path.join(MIGRATIONS_DIR, rollbackName);
    
    if (!fs.existsSync(rollbackPath)) {
      throw new BadRequestError(`Rollback file ${rollbackName} not found`);
    }
    
    // Read rollback file
    const sql = await readFile(rollbackPath, 'utf8');
    
    logger.info(`Rolling back migration: ${migrationName}`);
    
    // Execute rollback
    const { error: rollbackError } = await client.rpc('run_sql', { sql }, {
      headers: {
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      }
    });
    
    if (rollbackError) {
      throw new Error(`Failed to rollback migration ${migrationName}: ${rollbackError.message}`);
    }
    
    // Delete migration record
    const { error: deleteError } = await client
      .from('migrations')
      .delete()
      .eq('id', lastMigration.id);
    
    if (deleteError) {
      throw new Error(`Failed to delete migration record: ${deleteError.message}`);
    }
    
    logger.info(`Rolled back migration: ${migrationName}`);
  } catch (error) {
    logger.error('Failed to rollback last migration:', error);
    throw error;
  }
}

module.exports = {
  runMigrations,
  applySpecificMigration,
  rollbackLastMigration,
  getAppliedMigrations,
  getPendingMigrations
};
