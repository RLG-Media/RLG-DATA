-- User Data Schema for RLG Data and RLG Fans
-- Ensures secure, structured, and scalable user data management with full compliance.

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    city VARCHAR(100),
    town VARCHAR(100),
    phone_number VARCHAR(50) UNIQUE,
    subscription_status VARCHAR(50) CHECK (subscription_status IN ('Active', 'Inactive', 'Banned', 'Trial')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE user_profiles (
    profile_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    profile_picture TEXT DEFAULT NULL,
    bio TEXT,
    preferences JSONB DEFAULT '{}'::JSONB,
    account_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    UNIQUE(user_id)
);

CREATE TABLE payment_details (
    payment_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    payment_method VARCHAR(100) CHECK (payment_method IN ('Credit Card', 'PayPal', 'PayFast', 'Crypto')),
    last_payment_date TIMESTAMP,
    next_billing_date TIMESTAMP,
    transaction_history JSONB DEFAULT '[]'::JSONB
);

CREATE TABLE user_activity (
    activity_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    location VARCHAR(255),
    additional_data JSONB DEFAULT NULL
);

CREATE TABLE security_logs (
    security_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    event_type VARCHAR(255) CHECK (event_type IN ('LOGIN_SUCCESS', 'LOGIN_FAILURE', 'PASSWORD_RESET', 'SECURITY_ALERT')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    additional_info JSONB DEFAULT NULL
);

CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    plan VARCHAR(50) CHECK (plan IN ('Weekly', 'Monthly', 'Yearly')),
    country_lock BOOLEAN DEFAULT FALSE,
    price DECIMAL(10,2) NOT NULL,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NOT NULL
);

-- Indexes for Optimization
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_user_activity ON user_activity(timestamp);
CREATE INDEX idx_security_logs ON security_logs(timestamp);

-- Automatically update timestamps
CREATE OR REPLACE FUNCTION update_timestamp_column() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_users
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp_column();

-- Ensures **comprehensive, automated, and compliant** user data management. 🚀
