-- PostgreSQL Database Initialization Script

-- 1. Create database read-only user
CREATE USER read_only_user WITH PASSWORD 'read_only_pass';

-- 2. Grant Connect privilege
GRANT CONNECT ON DATABASE ai_sql_db TO read_only_user;

-- 3. Grant schema usage
GRANT USAGE ON SCHEMA public TO read_only_user;

-- 4. Grant SELECT permission ONLY on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only_user;

-- 5. Grant SELECT permission ONLY on future tables created by admin
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO read_only_user;

-- 6. Revoke modification permissions explicitly
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, ALTER, DROP ON ALL TABLES IN SCHEMA public FROM read_only_user;
