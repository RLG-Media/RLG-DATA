<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Notification Templates for RLG Data">
    <title>Notification Templates</title>
    <link rel="stylesheet" href="styles.css">
    <style>
        /* Inline styles for notification-specific formatting */
        body {
            font-family: 'Roboto', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f9f9f9;
            color: #333;
        }
        .notification-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        .notification-card {
            width: calc(100% - 40px);
            max-width: 400px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 20px;
        }
        .notification-card h3 {
            margin: 0;
            font-size: 18px;
            color: #007bff;
        }
        .notification-card p {
            font-size: 14px;
            color: #555;
            margin: 10px 0 0;
        }
        .notification-card .timestamp {
            font-size: 12px;
            color: #999;
            margin-top: 10px;
        }
        .notification-card.info {
            border-left: 4px solid #007bff;
        }
        .notification-card.warning {
            border-left: 4px solid #ffcc00;
        }
        .notification-card.error {
            border-left: 4px solid #ff4d4d;
        }
        .notification-card.success {
            border-left: 4px solid #28a745;
        }
    </style>
</head>
<body>
    <header>
        <h1>Notification Templates</h1>
        <p>Reusable notification designs for alerts, updates, and messages.</p>
    </header>
    
    <section class="notification-container">
        <!-- Information Notification -->
        <div class="notification-card info">
            <h3>System Update Available</h3>
            <p>A new version of the system is now available. Please update to the latest version to enjoy new features and improvements.</p>
            <span class="timestamp">Timestamp: 2025-01-04 10:00 AM</span>
        </div>

        <!-- Warning Notification -->
        <div class="notification-card warning">
            <h3>Storage Limit Reached</h3>
            <p>Your account is nearing its storage limit. Consider upgrading your plan or deleting unnecessary files.</p>
            <span class="timestamp">Timestamp: 2025-01-04 10:05 AM</span>
        </div>

        <!-- Error Notification -->
        <div class="notification-card error">
            <h3>Payment Failed</h3>
            <p>Your recent payment attempt was unsuccessful. Please verify your payment details and try again.</p>
            <span class="timestamp">Timestamp: 2025-01-04 10:10 AM</span>
        </div>

        <!-- Success Notification -->
        <div class="notification-card success">
            <h3>Profile Updated Successfully</h3>
            <p>Your profile details have been updated successfully.</p>
            <span class="timestamp">Timestamp: 2025-01-04 10:15 AM</span>
        </div>
    </section>
    
    <footer>
        <p>&copy; 2025 RLG Data. All rights reserved.</p>
    </footer>

    <!-- Optional JS -->
    <script>
        // Example of dynamic notifications rendering
        const notifications = [
            {
                type: 'info',
                title: 'System Update Available',
                message: 'A new version of the system is now available. Please update to the latest version to enjoy new features and improvements.',
                timestamp: '2025-01-04 10:00 AM'
            },
            {
                type: 'warning',
                title: 'Storage Limit Reached',
                message: 'Your account is nearing its storage limit. Consider upgrading your plan or deleting unnecessary files.',
                timestamp: '2025-01-04 10:05 AM'
            },
            {
                type: 'error',
                title: 'Payment Failed',
                message: 'Your recent payment attempt was unsuccessful. Please verify your payment details and try again.',
                timestamp: '2025-01-04 10:10 AM'
            },
            {
                type: 'success',
                title: 'Profile Updated Successfully',
                message: 'Your profile details have been updated successfully.',
                timestamp: '2025-01-04 10:15 AM'
            }
        ];

        const container = document.querySelector('.notification-container');
        notifications.forEach(({ type, title, message, timestamp }) => {
            const card = document.createElement('div');
            card.classList.add('notification-card', type);
            card.innerHTML = `
                <h3>${title}</h3>
                <p>${message}</p>
                <span class="timestamp">Timestamp: ${timestamp}</span>
            `;
            container.appendChild(card);
        });
    </script>
</body>
</html>
