// utils.js

/**
 * Debounce Function
 * Limits the rate at which a function is executed.
 * @param {Function} func - The function to debounce.
 * @param {number} delay - The delay in milliseconds.
 * @returns {Function} - The debounced function.
 */
export function debounce(func, delay = 300) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Throttle Function
 * Ensures a function is executed at most once in a specified interval.
 * @param {Function} func - The function to throttle.
 * @param {number} limit - The interval in milliseconds.
 * @returns {Function} - The throttled function.
 */
export function throttle(func, limit = 300) {
    let lastFunc, lastRan;
    return function (...args) {
        const context = this;
        const now = Date.now();
        if (!lastRan) {
            func.apply(context, args);
            lastRan = now;
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(() => {
                if (now - lastRan >= limit) {
                    func.apply(context, args);
                    lastRan = now;
                }
            }, limit - (now - lastRan));
        }
    };
}

/**
 * Format Date
 * Formats a date into a readable string.
 * @param {string|Date} date - The date to format.
 * @returns {string} - The formatted date string.
 */
export function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}

/**
 * Generate Random ID
 * Creates a unique identifier.
 * @param {number} length - Length of the ID.
 * @returns {string} - The random ID.
 */
export function generateRandomId(length = 8) {
    return Math.random().toString(36).substring(2, 2 + length);
}

/**
 * Copy to Clipboard
 * Copies a string to the clipboard.
 * @param {string} text - The text to copy.
 * @returns {Promise<void>}
 */
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        console.log("Text copied to clipboard:", text);
    } catch (error) {
        console.error("Failed to copy text:", error);
    }
}

/**
 * Smooth Scroll to Element
 * Scrolls smoothly to a specified element.
 * @param {string} selector - The selector of the target element.
 */
export function smoothScrollTo(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: "smooth" });
    } else {
        console.error(`Element not found: ${selector}`);
    }
}

/**
 * Check if Element is in Viewport
 * Determines if an element is visible in the viewport.
 * @param {HTMLElement} element - The element to check.
 * @returns {boolean} - True if in viewport, false otherwise.
 */
export function isElementInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Parse URL Parameters
 * Extracts query parameters from a URL.
 * @param {string} url - The URL to parse.
 * @returns {Object} - An object containing the key-value pairs.
 */
export function parseUrlParams(url = window.location.href) {
    const params = new URL(url).searchParams;
    const result = {};
    for (const [key, value] of params.entries()) {
        result[key] = value;
    }
    return result;
}

/**
 * Capitalize String
 * Capitalizes the first letter of a string.
 * @param {string} str - The string to capitalize.
 * @returns {string} - The capitalized string.
 */
export function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
}
