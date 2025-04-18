-- Rollback for Supabase Functions Migration
-- This script rolls back the Supabase functions migration

-- Drop functions
DROP FUNCTION IF EXISTS run_sql;
DROP FUNCTION IF EXISTS create_migrations_table;
DROP FUNCTION IF EXISTS check_table_exists;
