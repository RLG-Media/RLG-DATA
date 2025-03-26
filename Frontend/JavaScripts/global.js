/**
 * global.js
 * Centralized global utility functions and configurations for RLG Data and RLG Fans.
 */

// Configuration Constants
const CONFIG = {
  API_BASE_URL: "/api/v1", // Base API endpoint
  SUPPORTED_LANGUAGES: ["en", "es", "fr", "he"], // Supported languages
  DEFAULT_LANGUAGE: "en", // Default language
  THEME: "light", // Default theme
};

// Helper Functions
const Helpers = {
  /**
   * Fetch data from a given API endpoint.
   * @param {string} endpoint - API endpoint to fetch.
   * @param {string} method - HTTP method (GET, POST, PUT, DELETE).
   * @param {Object} body - Request body (for POST/PUT).
   * @returns {Promise<Object>} - Response data as JSON.
   */
  async fetchData(endpoint, method = "GET", body = null) {
    try {
      const headers = {
        "Content-Type": "application/json",
      };

      const options = {
        method,
        headers,
      };

      if (body) {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, options);
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error in fetchData: ${error.message}`);
      return null;
    }
  },

  /**
   * Toggle the theme between light and dark modes.
   */
  toggleTheme() {
    const root = document.documentElement;
    const currentTheme = root.getAttribute("data-theme") || CONFIG.THEME;

    const newTheme = currentTheme === "light" ? "dark" : "light";
    root.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);

    console.log(`Theme switched to: ${newTheme}`);
  },

  /**
   * Retrieve user-selected theme from localStorage.
   */
  initializeTheme() {
    const savedTheme = localStorage.getItem("theme") || CONFIG.THEME;
    document.documentElement.setAttribute("data-theme", savedTheme);
  },

  /**
   * Get a translated string based on key and selected language.
   * @param {string} key - Translation key.
   * @param {string} [lang=CONFIG.DEFAULT_LANGUAGE] - Language code.
   * @returns {string} - Translated string.
   */
  translate(key, lang = CONFIG.DEFAULT_LANGUAGE) {
    const translations = {
      en: {
        welcome: "Welcome",
        error: "An error occurred",
      },
      es: {
        welcome: "Bienvenido",
        error: "Ocurrió un error",
      },
      fr: {
        welcome: "Bienvenue",
        error: "Une erreur s'est produite",
      },
      he: {
        welcome: "ברוך הבא",
        error: "אירעה שגיאה",
      },
    };

    return translations[lang]?.[key] || translations[CONFIG.DEFAULT_LANGUAGE][key];
  },

  /**
   * Debounce a function to limit execution frequency.
   * @param {Function} func - Function to debounce.
   * @param {number} delay - Delay in milliseconds.
   * @returns {Function} - Debounced function.
   */
  debounce(func, delay) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => func.apply(this, args), delay);
    };
  },
};

// Global Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  // Initialize theme
  Helpers.initializeTheme();

  // Attach theme toggle event
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", Helpers.toggleTheme);
  }

  console.log("Global.js initialized.");
});

// Export as module (for future scalability and modularity)
export default {
  CONFIG,
  Helpers,
};
