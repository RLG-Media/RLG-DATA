#!/bin/bash
# backup_restore.sh
# ----------------------------
# RLG Data & RLG Fans Backup and Restore Script
#
# Author: RLG Team
#
# Description:
#   This script automates backup and restore procedures for the RLG Data & RLG Fans platform.
#   It backs up databases as well as application files for both tools.
#
#   Key Features:
#     - Backs up PostgreSQL databases with pg_dump.
#     - Archives application files (e.g., from /var/www/rlg_data and optionally /var/www/rlg_fans).
#     - Logs every step with timestamps for auditing and troubleshooting.
#     - Copies backups to remote storage if a remote directory is configured.
#     - Can be extended to include additional components (such as logs for scraping, compliance, AI insights,
#       report generators, monetization strategies, RLG newsletter, RLG Agent Chat Bot, and the RLG Super Tool).
#
# Usage:
#   backup_restore.sh backup
#   backup_restore.sh restore <timestamp>
# ----------------------------

# Configuration
BACKUP_DIR="/var/backups/rlg_data"
DATABASE_NAME="rlg_database"        # Primary database (RLG Data)
DATABASE_NAME_FANS="rlg_fans"         # Secondary database for RLG Fans (if applicable)
DATABASE_USER="rlg_admin"
REMOTE_STORAGE="/mnt/remote_backup"   # Optional remote backup directory
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="/var/log/backup_restore.log"

# Directories to backup (adjust or add paths as needed)
APP_DIR_DATA="/var/www/rlg_data"
APP_DIR_FANS="/var/www/rlg_fans"

# Ensure the backup directory exists
mkdir -p "$BACKUP_DIR"

# Log function to output messages to both stdout and log file
log_message() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# Function to backup the databases and application files
backup() {
    log_message "[INFO] Starting backup process at $TIMESTAMP"

    # Back up the primary database (RLG Data)
    pg_dump -U "$DATABASE_USER" "$DATABASE_NAME" > "$BACKUP_DIR/db_backup_${TIMESTAMP}.sql"
    if [ $? -eq 0 ]; then
        log_message "[SUCCESS] Primary database backup completed."
    else
        log_message "[ERROR] Primary database backup failed!"
        exit 1
    fi

    # If applicable, back up the secondary database (RLG Fans)
    pg_dump -U "$DATABASE_USER" "$DATABASE_NAME_FANS" > "$BACKUP_DIR/db_fans_backup_${TIMESTAMP}.sql"
    if [ $? -eq 0 ]; then
        log_message "[SUCCESS] Secondary database (RLG Fans) backup completed."
    else
        log_message "[WARNING] Secondary database backup failed (if not required, ignore)."
    fi

    # Back up application files for RLG Data
    tar -czf "$BACKUP_DIR/app_data_backup_${TIMESTAMP}.tar.gz" "$APP_DIR_DATA"
    if [ $? -eq 0 ]; then
        log_message "[SUCCESS] Application files (RLG Data) backup completed."
    else
        log_message "[ERROR] Application files (RLG Data) backup failed!"
        exit 1
    fi

    # Back up application files for RLG Fans, if available
    if [ -d "$APP_DIR_FANS" ]; then
        tar -czf "$BACKUP_DIR/app_fans_backup_${TIMESTAMP}.tar.gz" "$APP_DIR_FANS"
        if [ $? -eq 0 ]; then
            log_message "[SUCCESS] Application files (RLG Fans) backup completed."
        else
            log_message "[WARNING] Application files (RLG Fans) backup failed, but continuing."
        fi
    fi

    # Optional: Back up additional files (e.g. scraping logs, compliance reports)
    # tar -czf "$BACKUP_DIR/extra_backup_${TIMESTAMP}.tar.gz" /path/to/extra_files

    # Copy all backups to remote storage if configured
    if [ -d "$REMOTE_STORAGE" ]; then
        cp "$BACKUP_DIR"/* "$REMOTE_STORAGE"/
        log_message "[INFO] All backups copied to remote storage at $REMOTE_STORAGE."
    else
        log_message "[INFO] No remote storage detected; skipping remote copy."
    fi

    log_message "[INFO] Backup process completed successfully at $TIMESTAMP"
}

# Function to restore backup from a given timestamp
restore() {
    if [ -z "$1" ]; then
        log_message "[ERROR] No backup timestamp provided! Usage: restore <timestamp>"
        exit 1
    fi

    local RESTORE_TIMESTAMP=$1
    log_message "[INFO] Starting restore process for timestamp: $RESTORE_TIMESTAMP"

    # Restore primary database (RLG Data)
    if [ -f "$BACKUP_DIR/db_backup_${RESTORE_TIMESTAMP}.sql" ]; then
        psql -U "$DATABASE_USER" "$DATABASE_NAME" < "$BACKUP_DIR/db_backup_${RESTORE_TIMESTAMP}.sql"
        if [ $? -eq 0 ]; then
            log_message "[SUCCESS] Primary database restored successfully."
        else
            log_message "[ERROR] Primary database restore failed!"
            exit 1
        fi
    else
        log_message "[ERROR] Primary database backup file not found for timestamp: $RESTORE_TIMESTAMP"
        exit 1
    fi

    # Restore secondary database (RLG Fans) if applicable
    if [ -f "$BACKUP_DIR/db_fans_backup_${RESTORE_TIMESTAMP}.sql" ]; then
        psql -U "$DATABASE_USER" "$DATABASE_NAME_FANS" < "$BACKUP_DIR/db_fans_backup_${RESTORE_TIMESTAMP}.sql"
        if [ $? -eq 0 ]; then
            log_message "[SUCCESS] Secondary database (RLG Fans) restored successfully."
        else
            log_message "[WARNING] Secondary database restore failed (if not required, ignore)."
        fi
    fi

    # Restore application files for RLG Data
    if [ -f "$BACKUP_DIR/app_data_backup_${RESTORE_TIMESTAMP}.tar.gz" ]; then
        tar -xzf "$BACKUP_DIR/app_data_backup_${RESTORE_TIMESTAMP}.tar.gz" -C "$APP_DIR_DATA"
        if [ $? -eq 0 ]; then
            log_message "[SUCCESS] Application files (RLG Data) restored successfully."
        else
            log_message "[ERROR] Application files restore for RLG Data failed!"
            exit 1
        fi
    else
        log_message "[ERROR] Application backup file for RLG Data not found for timestamp: $RESTORE_TIMESTAMP"
        exit 1
    fi

    # Restore application files for RLG Fans if available
    if [ -f "$BACKUP_DIR/app_fans_backup_${RESTORE_TIMESTAMP}.tar.gz" ]; then
        tar -xzf "$BACKUP_DIR/app_fans_backup_${RESTORE_TIMESTAMP}.tar.gz" -C "$APP_DIR_FANS"
        if [ $? -eq 0 ]; then
            log_message "[SUCCESS] Application files (RLG Fans) restored successfully."
        else
            log_message "[WARNING] Application files restore for RLG Fans failed, but continuing."
        fi
    fi

    log_message "[INFO] Restore process completed successfully for timestamp: $RESTORE_TIMESTAMP"
}

# Main script execution block
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
