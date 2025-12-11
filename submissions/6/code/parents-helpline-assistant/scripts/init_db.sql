-- Initialize database with extensions and basic configuration
-- This file is automatically executed when the PostgreSQL container starts

-- Enable UUID extension (for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';
