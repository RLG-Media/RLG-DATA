// global_settings.js

// Define global constants and settings for both RLG Data and RLG Fans
const GlobalSettings = {
    // Backend API Endpoints
    apiBaseUrl: process.env.NODE_ENV === 'production' 
                ? 'https://your-production-url.com/api' 
                : 'http://localhost:5000/api',
                
    // Default platform settings
    platforms: [
        'OnlyFans', 'Patreon', 'Fansly', 'FanCentro', 'Fanfix', 'Fapello', 
        'ManyVids', 'Snapchat', 'TikTok', 'YouTube', 'Facebook', 'Instagram', 
        'Twitter', 'Reddit', 'Sheer', 'FeetFinder', 'Alua', 'YouFanly', 
        'Fansify', 'Pornhub'
    ],

    // Authentication Settings
    auth: {
        tokenKey: 'authToken',  // Key to store the JWT token in local storage
        refreshInterval: 60 * 60 * 1000, // 1-hour refresh interval for tokens
    },

    // User Interface Settings
    ui: {
        theme: {
            light: {
                backgroundColor: '#f8f9fa',
                primaryColor: '#007bff',
                textColor: '#343a40',
                sidebarColor: '#343a40',
            },
            dark: {
                backgroundColor: '#343a40',
                primaryColor: '#007bff',
                textColor: '#f8f9fa',
                sidebarColor: '#212529',
            },
            defaultTheme: 'light',
        },
        refreshIntervals: {
            engagementData: 30000, // 30 seconds for engagement widgets
            analytics: 60000,      // 1 minute for analytics widgets
        },
    },

    // Real-time WebSocket settings
    websocket: {
        url: process.env.NODE_ENV === 'production' 
             ? 'wss://your-production-url.com/socket' 
             : 'ws://localhost:5000/socket',
        retryInterval: 5000, // Retry connection every 5 seconds if disconnected
    },

    // API Request Timeout
    requestTimeout: 10000, // 10 seconds

    // Global Error Handling Messages
    errorMessages: {
        networkError: "Network error, please check your internet connection.",
        unauthorized: "You are not authorized to access this content. Please log in.",
        serverError: "Server error, please try again later.",
    },

    // Data Fetching and API Routes for RLG services
    endpoints: {
        fetchEngagement: (platform) => `/engagement/${platform}`,
        fetchUserStats: '/user/stats',
        contentScheduling: '/scheduling/content',
        recommendationEngine: '/recommendations',
        trendPredictor: '/trends/predict',
        aiContentAnalysis: '/content/analyze',
        rateLimitCheck: '/security/rate-limit',
        platformSettings: '/settings/platforms',
    },

    // Notification and Alert Settings
    notifications: {
        enableSound: true,
        displayDuration: 5000, // Display notifications for 5 seconds
    },

    // Global Debugging and Development Flags
    debug: {
        enableLogging: process.env.NODE_ENV !== 'production',
        showAlerts: process.env.NODE_ENV !== 'production',
    }
};

// Function to get the appropriate theme settings
export const getThemeSettings = (theme = GlobalSettings.ui.theme.defaultTheme) => {
    return GlobalSettings.ui.theme[theme] || GlobalSettings.ui.theme.light;
};

// Utility function to log messages if debugging is enabled
export const logDebug = (message, data = {}) => {
    if (GlobalSettings.debug.enableLogging) {
        console.log(`[DEBUG]: ${message}`, data);
    }
};

// Export global settings as default
export default GlobalSettings;
