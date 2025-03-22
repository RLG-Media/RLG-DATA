-- Data Migration Script for RLG Data and RLG Fans
-- This script ensures data consistency, adds missing tables, updates existing schemas,
-- and migrates legacy data to the latest structure.

-- Ensure a transactional migration
BEGIN;

-- 1. Add Missing Tables
CREATE TABLE IF NOT EXISTS archived_data (
    archive_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL,
    data_content JSONB NOT NULL,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    preference_key VARCHAR(100) NOT NULL,
    preference_value JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Update Existing Tables
-- Add new columns if they do not exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'phone_number'
    ) THEN
        ALTER TABLE users ADD COLUMN phone_number VARCHAR(15);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'profile_picture_url'
    ) THEN
        ALTER TABLE users ADD COLUMN profile_picture_url TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'logs' AND column_name = 'ip_address'
    ) THEN
        ALTER TABLE logs ADD COLUMN ip_address VARCHAR(45);
    END IF;
END $$;

-- 3. Migrate Legacy Data
-- Example: Move outdated preferences to the new user_preferences table
INSERT INTO user_preferences (user_id, preference_key, preference_value)
SELECT user_id, 'legacy_preference', to_jsonb(legacy_column)
FROM legacy_table
WHERE NOT EXISTS (
    SELECT 1 FROM user_preferences
    WHERE user_preferences.user_id = legacy_table.user_id
);

-- 4. Data Cleanup
-- Remove duplicate entries in analytics_data
DELETE FROM analytics_data
WHERE ctid NOT IN (
    SELECT MIN(ctid)
    FROM analytics_data
    GROUP BY user_id, data_type, collected_at
);

-- Remove orphaned entries in related tables
DELETE FROM user_roles
WHERE user_id NOT IN (SELECT user_id FROM users);

DELETE FROM user_permissions
WHERE user_id NOT IN (SELECT user_id FROM users);

-- 5. Index Optimization
-- Add missing indexes for improved performance
CREATE INDEX IF NOT EXISTS idx_archived_data_user ON archived_data (user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences (user_id);
CREATE INDEX IF NOT EXISTS idx_logs_ip_address ON logs (ip_address);

-- 6. Views and Triggers
-- Update existing views
CREATE OR REPLACE VIEW user_analytics_summary AS
SELECT
    user_id,
    COUNT(data_id) AS total_data_entries,
    MAX(collected_at) AS last_entry
FROM analytics_data
GROUP BY user_id;

-- Add trigger for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_user_preferences_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_user_preferences_updated ON user_preferences;
CREATE TRIGGER trg_user_preferences_updated
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION update_user_preferences_timestamp();

-- 7. Audit and Logging Enhancements
-- Add audit logs for data migrations
INSERT INTO logs (log_level, message, timestamp)
VALUES ('INFO', 'Data migration completed successfully.', CURRENT_TIMESTAMP);

-- Commit all changes
COMMIT;
