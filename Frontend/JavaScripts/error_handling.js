/**
 * error_handling.js
 * Comprehensive error handling for RLG Data and RLG Fans.
 * Ensures logging, tracking, and user-friendly feedback for all errors.
 */

// Import dependencies
import Sentry from '@sentry/browser'; // For error tracking
import { notifyUser } from './notifications'; // Custom notification system
import { logError } from './logging'; // Custom logging utility

// Initialize Sentry for centralized error tracking
Sentry.init({
    dsn: 'https://examplePublicKey@o0.ingest.sentry.io/0',
    environment: process.env.NODE_ENV || 'development',
    tracesSampleRate: 1.0,
    release: 'rlg-project@1.0.0',
});

/**
 * Custom Error Class for Application-Specific Errors
 */
class AppError extends Error {
    constructor(message, code, isOperational = true) {
        super(message);
        this.name = 'AppError';
        this.code = code || 'UNSPECIFIED_ERROR';
        this.isOperational = isOperational;
        Error.captureStackTrace(this, this.constructor);
    }
}

/**
 * Global Error Handler
 * Handles all uncaught exceptions and rejected promises.
 */
function globalErrorHandler(error, source = 'Unknown') {
    const errorMessage = error.message || 'An unexpected error occurred.';
    const errorCode = error.code || 'UNKNOWN_ERROR';
    const errorStack = error.stack || 'No stack trace available.';
    const isOperational = error.isOperational || false;

    // Log error details
    logError({
        message: errorMessage,
        code: errorCode,
        stack: errorStack,
        source,
        isOperational,
    });

    // Send error to Sentry
    Sentry.captureException(error, {
        tags: {
            source,
            environment: process.env.NODE_ENV || 'development',
        },
    });

    // Notify user if the error is operational
    if (isOperational) {
        notifyUser({
            type: 'error',
            message: `An error occurred: ${errorMessage}`,
        });
    } else {
        // Display generic message for non-operational errors
        notifyUser({
            type: 'error',
            message: 'Something went wrong. Please try again later.',
        });
    }
}

/**
 * Wrapper for Async Functions
 * Automatically catches and handles errors in async/await functions.
 */
function asyncHandler(fn) {
    return function (req, res, next) {
        Promise.resolve(fn(req, res, next)).catch((err) => globalErrorHandler(err, 'AsyncHandler'));
    };
}

/**
 * Event Listener for Uncaught Errors
 * Captures global uncaught errors and unhandled promise rejections.
 */
window.addEventListener('error', (event) => {
    globalErrorHandler(event.error || new Error('Uncaught Error'), 'GlobalListener');
});

window.addEventListener('unhandledrejection', (event) => {
    globalErrorHandler(event.reason || new Error('Unhandled Promise Rejection'), 'GlobalListener');
});

/**
 * Example Usage of Error Handling
 */
function exampleFunction() {
    try {
        // Simulate a runtime error
        throw new AppError('This is a simulated error', 'SIMULATED_ERROR');
    } catch (error) {
        globalErrorHandler(error, 'exampleFunction');
    }
}

// Execute exampleFunction to demonstrate error handling
exampleFunction();

/**
 * Exported Utilities
 * These utilities can be reused throughout the project.
 */
export { AppError, globalErrorHandler, asyncHandler };
