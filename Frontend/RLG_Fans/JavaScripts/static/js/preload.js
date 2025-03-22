// preload.js
// Preload script for RLG Data and RLG Fans
// This script preloads essential configuration and geolocation data before the main app loads.

(function() {
    'use strict';
  
    // Configure logging for debugging purposes.
    const log = console.log.bind(console);
    const error = console.error.bind(console);
  
    // Global configuration object.
    // In production, you might inject these values from environment variables or server-side rendered JSON.
    window.APP_CONFIG = {
      apiBaseUrl: "https://api.example.com", // Replace with your actual API base URL
      defaultLocale: "en_US",
      // Additional configuration options can be added here.
    };
  
    // Global object to store user geolocation details.
    window.USER_GEOLOCATION = null;
  
    /**
     * Fetch geolocation information using an external API.
     * This function calls ipapi.co to retrieve region, country, city, and town details.
     */
    async function fetchGeolocation() {
      try {
        const response = await fetch("https://ipapi.co/json/");
        if (!response.ok) {
          throw new Error(`Failed to fetch geolocation data: ${response.status}`);
        }
        const data = await response.json();
        window.USER_GEOLOCATION = {
          region: data.region || null,
          country: data.country_name || null,
          city: data.city || null,
          // "Town" may not be provided by ipapi.co; using region as a fallback.
          town: data.region || null,
        };
        log("Geolocation data fetched successfully:", window.USER_GEOLOCATION);
      } catch (err) {
        error("Error fetching geolocation data:", err);
        window.USER_GEOLOCATION = null;
      }
    }
  
    /**
     * Initialize the preload process.
     * This function runs asynchronous tasks that need to be completed before the main app loads.
     */
    async function initPreload() {
      log("Initializing preload script for RLG Data and RLG Fans...");
      await fetchGeolocation();
      // Additional preload tasks (e.g., fetching user settings, available tools) can be added here.
      log("Preload initialization complete.");
    }
  
    // Start the initialization.
    initPreload().catch(err => {
      error("Initialization error in preload.js:", err);
    });
  
    // Expose helper functions and global variables for use in your main application.
    window.getUserGeo = function() {
      return window.USER_GEOLOCATION;
    };
  
    /**
     * Update the global application configuration.
     * @param {Object} newConfig - An object containing configuration updates.
     */
    window.updateAppConfig = function(newConfig) {
      window.APP_CONFIG = { ...window.APP_CONFIG, ...newConfig };
      log("Application configuration updated:", window.APP_CONFIG);
    };
  
    // Final log message to indicate that the preload script has finished executing.
    log("Preload script execution completed.");
  })();
  