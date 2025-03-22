-- RLG Media Archive Database Schema
-- Ensures robust, scalable, and efficient storage for RLG Data and RLG Fans media content

CREATE DATABASE IF NOT EXISTS rlg_media_archive;
USE rlg_media_archive;

-- Table to store media files
CREATE TABLE media_files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type ENUM('image', 'video', 'audio', 'document') NOT NULL,
    file_size BIGINT NOT NULL,
    file_path TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    compliance_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    metadata JSON,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Table to track compliance reviews
CREATE TABLE compliance_reviews (
    id SERIAL PRIMARY KEY,
    media_id INT NOT NULL,
    reviewed_by VARCHAR(255) NOT NULL,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('approved', 'rejected') NOT NULL,
    comments TEXT,
    FOREIGN KEY (media_id) REFERENCES media_files(id) ON DELETE CASCADE
);

-- Table to store AI-driven tagging and categorization
CREATE TABLE media_tags (
    id SERIAL PRIMARY KEY,
    media_id INT NOT NULL,
    tag VARCHAR(255) NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (media_id) REFERENCES media_files(id) ON DELETE CASCADE
);

-- Indexing for performance optimization
CREATE INDEX idx_media_region ON media_files(region, country, city);
CREATE INDEX idx_compliance_status ON media_files(compliance_status);
CREATE INDEX idx_tags_media_id ON media_tags(media_id);

-- View to get media with compliance status
CREATE VIEW media_compliance_view AS
SELECT 
    mf.id, mf.file_name, mf.file_type, mf.uploaded_by, mf.upload_date, 
    mf.region, mf.country, mf.city, mf.compliance_status, 
    cr.review_date, cr.status AS review_status, cr.comments
FROM media_files mf
LEFT JOIN compliance_reviews cr ON mf.id = cr.media_id;

-- Triggers for automated compliance updates
DELIMITER $$
CREATE TRIGGER after_media_upload
AFTER INSERT ON media_files
FOR EACH ROW
BEGIN
    INSERT INTO compliance_reviews (media_id, reviewed_by, status, comments)
    VALUES (NEW.id, 'System', 'pending', 'Awaiting review');
END $$
DELIMITER ;
