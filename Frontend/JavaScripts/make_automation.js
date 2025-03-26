#!/usr/bin/env node

/**
 * make_automation.js
 *
 * This script acts as a command-line tool to trigger automated tasks
 * for RLG Data and RLG Fans. It supports tasks such as:
 *   - Backup: Create a full backup of the specified data directory.
 *   - Report: Generate and export a combined report.
 *   - RefreshIntegrations: Refresh integration tokens or connection details.
 *   - Performance: Run performance monitoring checks.
 *   - Pipeline: Trigger the full automation pipeline (backup, report, refresh, performance).
 *
 * Usage:
 *   node make_automation.js --task <task> [--dataDir <path>]
 *   Example: node make_automation.js --task backup --dataDir "/path/to/data"
 */

const axios = require('axios');
const { program } = require('commander');
const winston = require('winston');

// Create a logger using Winston
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.printf(info => `${info.timestamp} | ${info.level.toUpperCase()} | ${info.message}`)
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'automation.log' })
  ]
});

// Define the automation API endpoint (adjust or load from environment variables as needed)
const AUTOMATION_API_URL = process.env.AUTOMATION_API_URL || 'http://localhost:5000/automation/run';

// Set up command-line options using Commander
program
  .version('1.0.0')
  .description('Automation Task Runner for RLG Data & RLG Fans')
  .requiredOption('-t, --task <task>', 'Task to run (backup, report, refreshIntegrations, performance, pipeline)')
  .option('-d, --dataDir <dataDir>', 'Data directory for backup tasks', '')
  // You can add more options (e.g., region, country, etc.) as needed.
  .parse(process.argv);

const options = program.opts();
const task = options.task;
const dataDir = options.dataDir;

// Prepare payload for the backend automation endpoint
const payload = {
  task: task,
  data_dir: dataDir,
  timestamp: new Date().toISOString()
};

logger.info(`Triggering automation task: ${task}`);

// Trigger the automation task via an HTTP POST request
axios.post(AUTOMATION_API_URL, payload, { timeout: 15000 })
  .then(response => {
    logger.info(`Task '${task}' executed successfully. Response: ${JSON.stringify(response.data)}`);
    process.exit(0);
  })
  .catch(error => {
    let errorMsg = error.response 
      ? `Status ${error.response.status} - ${JSON.stringify(error.response.data)}`
      : error.message;
    logger.error(`Error executing task '${task}': ${errorMsg}`);
    process.exit(1);
  });
