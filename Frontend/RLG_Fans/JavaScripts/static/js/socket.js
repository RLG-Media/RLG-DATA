// Initialize WebSocket connection
const socket = io.connect(window.location.origin);

// Event listeners for WebSocket connection events
socket.on('connect', () => {
    console.log('Connected to WebSocket');
});

socket.on('disconnect', () => {
    console.log('Disconnected from WebSocket');
});

// Handler for incoming notifications
socket.on('notification', (data) => {
    displayNotification(data.title, data.message);
});

// Display real-time notifications
function displayNotification(title, message) {
    const notificationContainer = document.getElementById('notification-container');
    if (notificationContainer) {
        const notification = document.createElement('div');
        notification.className = 'notification-banner';
        notification.innerHTML = `<strong>${title}</strong><p>${message}</p>`;
        notificationContainer.appendChild(notification);

        // Auto-dismiss notification after 5 seconds
        setTimeout(() => {
            notificationContainer.removeChild(notification);
        }, 5000);
    }
}

// Real-time updates for mentions chart
socket.on('mentions_update', (data) => {
    updateMentionsChart(data);
});

// Real-time updates for sentiment analysis chart
socket.on('sentiment_update', (data) => {
    updateSentimentChart(data);
});

// Real-time updates for engagement rates
socket.on('engagement_update', (data) => {
    updateEngagementChart(data.values, data.labels);
});

// Listen for custom real-time updates for TikTok analytics
socket.on('tiktok_analytics', (data) => {
    displayNotification(`TikTok Analytics Update`, `New insights available: ${data.message}`);
    updateTikTokAnalyticsChart(data.analyticsData); // Ensure this chart is defined in charts.js
});

// Listen for Zapier-triggered events
socket.on('zapier_event', (data) => {
    displayNotification(`Zapier Event Triggered`, `Event: ${data.event_name}, Details: ${data.details}`);
});

// Listen for API key expiration alerts
socket.on('api_key_expiration', (data) => {
    displayNotification(`API Key Expiration Warning`, `Your API key for ${data.platform} expires on ${data.expiration_date}. Please update it.`);
});

// Custom alert handler for content trends and engagement
socket.on('content_trend', (data) => {
    displayNotification(`Trending on ${data.platform}`, data.content);
});

socket.on('engagement_alert', (data) => {
    displayNotification(`Engagement Rate Update on ${data.platform}`, `New engagement rate: ${data.engagement_rate}%`);
});

// Custom function to send user-triggered events (e.g., manual refresh)
function sendUserEvent(eventName, eventData) {
    socket.emit(eventName, eventData);
    console.log(`Event "${eventName}" sent with data:`, eventData);
}

// Real-time updates for cross-platform analytics
socket.on('cross_platform_analytics', (data) => {
    displayNotification(`Cross-Platform Analytics Update`, `New data available across ${data.platforms.join(", ")}`);
    updateCrossPlatformAnalytics(data.analyticsData); // Ensure this chart or visualization is implemented
});

// Chart update functions (assumes charts are defined in charts.js)
function updateMentionsChart(data) {
    console.log('Updating mentions chart with:', data);
    // Implement chart update logic
}

function updateSentimentChart(data) {
    console.log('Updating sentiment chart with:', data);
    // Implement chart update logic
}

function updateEngagementChart(values, labels) {
    console.log('Updating engagement chart with values:', values, 'and labels:', labels);
    // Implement chart update logic
}

function updateTikTokAnalyticsChart(data) {
    console.log('Updating TikTok analytics chart with:', data);
    // Implement chart update logic for TikTok analytics
}

function updateCrossPlatformAnalytics(data) {
    console.log('Updating cross-platform analytics with:', data);
    // Implement chart or visualization update logic for cross-platform analytics
}
