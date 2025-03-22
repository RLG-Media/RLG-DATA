-- Drop tables if they already exist for a clean start (use carefully in dev/test environments)
DROP TABLE IF EXISTS users, roles, permissions, user_roles, user_permissions, analytics_data, reports, notifications, automations, logs, settings;

-- Create a table for user accounts
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Create a table for user roles
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- Create a table for permissions
CREATE TABLE permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- Create a mapping table for user roles
CREATE TABLE user_roles (
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    role_id INT REFERENCES roles(role_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id)
);

-- Create a mapping table for role permissions
CREATE TABLE user_permissions (
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    permission_id INT REFERENCES permissions(permission_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, permission_id)
);

-- Create a table for analytics data
CREATE TABLE analytics_data (
    data_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    data_type VARCHAR(50),
    data_content JSONB,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for reports
CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    report_name VARCHAR(100) NOT NULL,
    report_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for notifications
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(100),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for automation workflows
CREATE TABLE automations (
    automation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    automation_name VARCHAR(100) NOT NULL,
    workflow JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_run TIMESTAMP
);

-- Create a table for system logs
CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    log_level VARCHAR(50),
    message TEXT,
    user_id INT REFERENCES users(user_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for system settings
CREATE TABLE settings (
    setting_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX idx_user_email ON users (email);
CREATE INDEX idx_user_roles ON user_roles (user_id, role_id);
CREATE INDEX idx_role_permissions ON user_permissions (user_id, permission_id);
CREATE INDEX idx_analytics_data_user ON analytics_data (user_id, collected_at);
CREATE INDEX idx_reports_user ON reports (user_id, created_at);

-- Create views for aggregated analytics
CREATE VIEW user_analytics_summary AS
SELECT
    user_id,
    COUNT(data_id) AS total_data_entries,
    MAX(collected_at) AS last_entry
FROM analytics_data
GROUP BY user_id;

-- Add triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Add recommendations for scaling
-- 1. Use partitioning for large tables like `analytics_data` for performance.
-- 2. Implement archival strategies for old logs and analytics data.
-- 3. Add auditing tables to track changes in critical tables.
-- 4. Consider caching frequently accessed data using Redis or Memcached.
-- 5. Integrate full-text search for tables like `notifications` and `reports` for better user experience.
-- 6. Add database-level encryption for sensitive fields, such as `password_hash`.
-- 7. Implement role-based access controls for each table.

-- Commit all changes
COMMIT;
