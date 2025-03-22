-- Log Tracking Database Schema for RLG Data and RLG Fans
-- Ensures robust logging of system events, user activities, API calls, and security compliance.

CREATE TABLE system_logs (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    log_level VARCHAR(50) NOT NULL CHECK (log_level IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG')),
    message TEXT NOT NULL,
    module VARCHAR(100) NOT NULL,
    stack_trace TEXT,
    ip_address VARCHAR(45),
    user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
    metadata JSONB DEFAULT NULL
);

CREATE TABLE user_activity_logs (
    activity_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    location VARCHAR(255),
    additional_data JSONB DEFAULT NULL
);

CREATE TABLE api_call_logs (
    api_log_id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_code INT NOT NULL,
    response_time_ms INT,
    user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
    ip_address VARCHAR(45),
    request_payload JSONB DEFAULT NULL,
    response_payload JSONB DEFAULT NULL
);

CREATE TABLE security_logs (
    security_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
    event_type VARCHAR(255) NOT NULL CHECK (event_type IN ('LOGIN_SUCCESS', 'LOGIN_FAILURE', 'ACCOUNT_LOCKED', 'PASSWORD_RESET', 'SECURITY_ALERT')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    additional_info JSONB DEFAULT NULL
);

-- Indexes for faster lookups
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX idx_user_activity_timestamp ON user_activity_logs(timestamp);
CREATE INDEX idx_api_logs_timestamp ON api_call_logs(timestamp);
CREATE INDEX idx_security_logs_timestamp ON security_logs(timestamp);

-- Log retention policy (Automatically delete logs older than 1 year)
CREATE OR REPLACE FUNCTION delete_old_logs() RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM system_logs WHERE timestamp < NOW() - INTERVAL '1 year';
    DELETE FROM user_activity_logs WHERE timestamp < NOW() - INTERVAL '1 year';
    DELETE FROM api_call_logs WHERE timestamp < NOW() - INTERVAL '1 year';
    DELETE FROM security_logs WHERE timestamp < NOW() - INTERVAL '1 year';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_cleanup_trigger
AFTER INSERT ON system_logs
EXECUTE FUNCTION delete_old_logs();

CREATE TRIGGER log_cleanup_trigger_activity
AFTER INSERT ON user_activity_logs
EXECUTE FUNCTION delete_old_logs();

CREATE TRIGGER log_cleanup_trigger_api
AFTER INSERT ON api_call_logs
EXECUTE FUNCTION delete_old_logs();

CREATE TRIGGER log_cleanup_trigger_security
AFTER INSERT ON security_logs
EXECUTE FUNCTION delete_old_logs();

-- Ensures comprehensive log tracking, retention policies, and compliance.
