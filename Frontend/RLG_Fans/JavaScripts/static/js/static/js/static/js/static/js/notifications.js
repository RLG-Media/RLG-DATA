// notifications.js

// WebSocket connection for real-time notifications
const socket = io.connect(window.location.origin);

// Event listeners for WebSocket connection
socket.on('connect', () => {
    console.log("Connected to notifications WebSocket.");
});

socket.on('disconnect', () => {
    console.log("Disconnected from notifications WebSocket.");
});

// Listen for notification messages from the server
socket.on('notification', (data) => {
    displayNotification(data);
});

// Function to display a notification in the UI
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

// Event handler for updating notification preferences
document.getElementById('notificationSettingsForm').addEventListener('submit', (event) => {
    event.preventDefault();

    const emailNotifications = document.getElementById('email_notifications').checked;
    const smsNotifications = document.getElementById('sms_notifications').checked;

    // Update user notification preferences
    fetch('/api/update_notifications', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        },
        body: JSON.stringify({
            email_notifications: emailNotifications,
            sms_notifications: smsNotifications
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Notification settings updated successfully.');
        } else {
            alert('Error updating notification settings.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating notification settings.');
    });
});
