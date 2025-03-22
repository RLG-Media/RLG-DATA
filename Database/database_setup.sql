-- Database Setup for RLG Data & RLG Fans
-- Ensures robust, scalable, and efficient database structure

CREATE DATABASE IF NOT EXISTS rlg_data;
USE rlg_data;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    city VARCHAR(100),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscription Plans Table
CREATE TABLE IF NOT EXISTS subscription_plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    duration ENUM('weekly', 'monthly') NOT NULL
);

-- Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    plan_id INT,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NOT NULL,
    status ENUM('active', 'expired', 'canceled') DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(plan_id) ON DELETE CASCADE
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(100),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'completed', 'failed') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Data Scraping Logs
CREATE TABLE IF NOT EXISTS scraping_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    source VARCHAR(255) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Compliance Audits
CREATE TABLE IF NOT EXISTS compliance_audits (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    compliance_check VARCHAR(255) NOT NULL,
    result ENUM('pass', 'fail') NOT NULL,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Alerts & Notifications
CREATE TABLE IF NOT EXISTS alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('sent', 'pending', 'failed') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexes for performance optimization
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_scraping_logs_user ON scraping_logs(user_id);
CREATE INDEX idx_compliance_audits_user ON compliance_audits(user_id);
CREATE INDEX idx_alerts_user ON alerts(user_id);

-- Sample Data Insertion
INSERT INTO subscription_plans (plan_name, price, duration) VALUES
    ('Israel Weekly Plan', 99.00, 'weekly'),
    ('Israel Monthly Plan', 99.00, 'monthly'),
    ('Global Weekly Plan', 15.00, 'weekly'),
    ('Global Monthly Plan', 59.00, 'monthly');
