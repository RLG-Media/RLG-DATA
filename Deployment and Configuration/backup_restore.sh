#!/bin/bash

# Backup and Restore Script for RLG Data and RLG Fans
# Author: RLG Team
# Description: Automated script to backup and restore databases and important files

# Configuration
BACKUP_DIR="/var/backups/rlg_data"
DATABASE_NAME="rlg_database"
DATABASE_USER="rlg_admin"
REMOTE_STORAGE="/mnt/remote_backup"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="/var/log/backup_restore.log"

# Ensure the backup directory exists
mkdir -p "$BACKUP_DIR"

# Function to perform backup
backup() {
    echo "[INFO] Starting backup at $TIMESTAMP" | tee -a "$LOG_FILE"
    
    # Backup database
    pg_dump -U "$DATABASE_USER" "$DATABASE_NAME" > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] Database backup completed." | tee -a "$LOG_FILE"
    else
        echo "[ERROR] Database backup failed!" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # Backup application files
    tar -czf "$BACKUP_DIR/app_backup_$TIMESTAMP.tar.gz" /var/www/rlg_data/
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] Application files backup completed." | tee -a "$LOG_FILE"
    else
        echo "[ERROR] Application files backup failed!" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # Move to remote storage if configured
    if [ -d "$REMOTE_STORAGE" ]; then
        cp "$BACKUP_DIR"/* "$REMOTE_STORAGE"/
        echo "[INFO] Backup copied to remote storage." | tee -a "$LOG_FILE"
    fi
}

# Function to restore from backup
restore() {
    if [ -z "$1" ]; then
        echo "[ERROR] No backup timestamp provided! Usage: restore <timestamp>" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    TIMESTAMP=$1
    echo "[INFO] Starting restore process for $TIMESTAMP" | tee -a "$LOG_FILE"
    
    # Restore database
    psql -U "$DATABASE_USER" "$DATABASE_NAME" < "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] Database restored successfully." | tee -a "$LOG_FILE"
    else
        echo "[ERROR] Database restore failed!" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # Restore application files
    tar -xzf "$BACKUP_DIR/app_backup_$TIMESTAMP.tar.gz" -C /var/www/rlg_data/
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] Application files restored successfully." | tee -a "$LOG_FILE"
    else
        echo "[ERROR] Application files restore failed!" | tee -a "$LOG_FILE"
        exit 1
    fi
}

# Main execution
case "$1" in
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    *)
        echo "Usage: $0 {backup|restore <timestamp>}" | tee -a "$LOG_FILE"
        exit 1
        ;;
esac
