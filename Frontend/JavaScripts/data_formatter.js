/**
 * Data Formatter Module
 * Provides utilities to format, normalize, validate, and prepare data for consistent use across the application.
 */

import Intl from 'intl'; // For currency and locale-based formatting

class DataFormatter {
  // Default configuration
  static config = {
    defaultDateFormat: "YYYY-MM-DD",
    defaultLocale: "en-US",
    defaultCurrency: "USD",
    csvDelimiter: ",",
  };

  /**
   * Configures default settings for the formatter.
   * @param {Object} options - Configuration options (e.g., { defaultDateFormat: "MM/DD/YYYY" }).
   */
  static configure(options = {}) {
    this.config = { ...this.config, ...options };
  }

  /**
   * Formats a given date into a specified format.
   *
   * @param {string|Date} date - The date to format.
   * @param {string} format - The desired format (e.g., "YYYY-MM-DD", "MM/DD/YYYY").
   * @returns {string} - The formatted date string.
   */
  static formatDate(date, format = this.config.defaultDateFormat) {
    const d = new Date(date);
    if (isNaN(d)) {
      throw new Error("Invalid date provided.");
    }

    const pad = (n) => (n < 10 ? `0${n}` : n);

    const map = {
      YYYY: d.getFullYear(),
      MM: pad(d.getMonth() + 1),
      DD: pad(d.getDate()),
      HH: pad(d.getHours()),
      mm: pad(d.getMinutes()),
      ss: pad(d.getSeconds()),
    };

    return format.replace(/YYYY|MM|DD|HH|mm|ss/g, (match) => map[match]);
  }

  /**
   * Normalizes text by trimming, converting to lowercase, and removing extra spaces.
   *
   * @param {string} text - The text to normalize.
   * @returns {string} - The normalized text.
   */
  static normalizeText(text) {
    if (typeof text !== "string") {
      throw new Error("Text must be a string.");
    }
    return text.trim().replace(/\s+/g, " ").toLowerCase();
  }

  /**
   * Formats numbers with locale-based settings for currency or general formatting.
   *
   * @param {number} number - The number to format.
   * @param {Object} options - Formatting options (e.g., { style: "currency", currency: "USD" }).
   * @returns {string} - The formatted number.
   */
  static formatNumber(number, options = { style: "decimal" }) {
    if (typeof number !== "number" || isNaN(number)) {
      throw new Error("Invalid number provided.");
    }
    return new Intl.NumberFormat(this.config.defaultLocale, options).format(
      number
    );
  }

  /**
   * Formats a number into a currency string.
   *
   * @param {number} amount - The amount to format.
   * @param {string} currency - The currency code (default is configured currency).
   * @returns {string} - The formatted currency string.
   */
  static formatCurrency(amount, currency = this.config.defaultCurrency) {
    return this.formatNumber(amount, {
      style: "currency",
      currency: currency,
    });
  }

  /**
   * Validates and formats an email address.
   *
   * @param {string} email - The email address to validate and format.
   * @returns {string} - The validated email address in lowercase.
   * @throws Will throw an error if the email is invalid.
   */
  static validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      throw new Error("Invalid email address.");
    }
    return email.trim().toLowerCase();
  }

  /**
   * Formats a phone number into a standard format (e.g., +1 (123) 456-7890).
   *
   * @param {string} phoneNumber - The phone number to format.
   * @returns {string} - The formatted phone number.
   */
  static formatPhoneNumber(phoneNumber) {
    const cleanNumber = phoneNumber.replace(/\D/g, "");
    if (cleanNumber.length === 10) {
      return cleanNumber.replace(
        /(\d{3})(\d{3})(\d{4})/,
        "($1) $2-$3"
      );
    } else if (cleanNumber.length === 11 && cleanNumber.startsWith("1")) {
      return cleanNumber.replace(
        /(\d)(\d{3})(\d{3})(\d{4})/,
        "+$1 ($2) $3-$4"
      );
    }
    throw new Error("Invalid phone number.");
  }

  /**
   * Converts a string into a slug (URL-friendly format).
   *
   * @param {string} text - The text to convert into a slug.
   * @returns {string} - The generated slug.
   */
  static toSlug(text) {
    if (typeof text !== "string") {
      throw new Error("Text must be a string.");
    }
    return text
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");
  }

  /**
   * Converts a JSON object into a formatted string with indentation.
   *
   * @param {Object} json - The JSON object to format.
   * @param {number} spaces - The number of spaces for indentation (default is 2).
   * @returns {string} - The formatted JSON string.
   */
  static formatJSON(json, spaces = 2) {
    try {
      return JSON.stringify(json, null, spaces);
    } catch (error) {
      throw new Error("Invalid JSON object.");
    }
  }

  /**
   * Sanitizes HTML input to prevent XSS attacks.
   *
   * @param {string} html - The HTML string to sanitize.
   * @returns {string} - The sanitized HTML string.
   */
  static sanitizeHTML(html) {
    const div = document.createElement("div");
    div.textContent = html;
    return div.innerHTML;
  }

  /**
   * Parses and formats CSV data into a structured JSON format.
   *
   * @param {string} csvData - The CSV string to parse.
   * @param {string} delimiter - The delimiter used in the CSV (default is configured delimiter).
   * @returns {Array<Object>} - The parsed data as an array of objects.
   */
  static parseCSV(csvData, delimiter = this.config.csvDelimiter) {
    const [headerLine, ...lines] = csvData.trim().split("\n");
    const headers = headerLine.split(delimiter);

    return lines.map((line) => {
      const values = line.split(delimiter);
      return headers.reduce(
        (obj, header, index) => ({ ...obj, [header]: values[index] }),
        {}
      );
    });
  }
}

export default DataFormatter;
