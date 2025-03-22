// socket.js

// Initialize the WebSocket connection
const socket = io.connect(window.location.origin);

// Event listeners for WebSocket connection
socket.on('connect', () => {
    console.log("Connected to the WebSocket server.");
});

socket.on('disconnect', () => {
    console.log("Disconnected from the WebSocket server.");
});

// Listen for general real-time updates
socket.on('update', (data) => {
    handleRealTimeUpdate(data);
});

// Listen for notification-specific updates
socket.on('notification', (data) => {
    displayNotification(data);
});

// Handle real-time updates (such as new comments, likes, etc.)
function handleRealTimeUpdate(data) {
    if (data.updateType === 'mentions') {
        updateMentionsGraph(data);
    } else if (data.updateType === 'sentiment') {
        updateSentimentGraph(data);
    } else if (data.updateType === 'trending') {
        updateTrendingContent(data);
    }
    console.log("Real-time update received:", data);
}

// Display notifications in the notification area
function displayNotification(data) {
    const notificationContainer = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = 'alert alert-info notification';
    notification.innerHTML = `
        <strong>${data.title}</strong><br>
        ${data.message}
        <button type="button" class="btn-close" onclick="removeNotification(this)"></button>
    `;
    notificationContainer.appendChild(notification);

    // Automatically remove the notification after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Function to remove notification on button click
function removeNotification(button) {
    const notification = button.parentElement;
    notification.remove();
}

// Real-time mentions graph update
function updateMentionsGraph(data) {
    const ctx = document.getElementById('mentionsGraph').getContext('2d');
    const mentionsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Mentions',
                data: data.values,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Real-time sentiment graph update
function updateSentimentGraph(data) {
    const ctx = document.getElementById('sentimentGraph').getContext('2d');
    const sentimentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Sentiment',
                data: data.values,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Update trending content display
function updateTrendingContent(data) {
    const trendingContainer = document.getElementById('trendingContainer');
    trendingContainer.innerHTML = '';  // Clear existing content

    data.items.forEach(item => {
        const trendingItem = document.createElement('div');
        trendingItem.className = 'trending-item';
        trendingItem.innerHTML = `
            <h5>${item.title}</h5>
            <p>${item.description}</p>
            <a href="${item.url}" target="_blank">Read more</a>
        `;
        trendingContainer.appendChild(trendingItem);
    });
}
