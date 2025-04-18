-- Rollback for Initial Schema Migration
-- This script rolls back the initial schema migration

-- Drop tables in reverse order to avoid foreign key constraints
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS api_keys;
DROP TABLE IF EXISTS financial_data;
DROP TABLE IF EXISTS financial_entities;
DROP TABLE IF EXISTS document_data;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS organization_users;
DROP TABLE IF EXISTS organizations;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS health_check;

-- Drop functions
DROP FUNCTION IF EXISTS is_member_of_organization;
