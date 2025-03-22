document.addEventListener("DOMContentLoaded", () => {
    // Constants for API and DOM elements
    const NOTIFICATIONS_API_ENDPOINT = "/api/notifications"; // Replace with your API endpoint
    const NOTIFICATION_LIST_CONTAINER = document.getElementById("notification-list");
    const NOTIFICATION_FORM = document.getElementById("notification-form");
    const SEARCH_INPUT = document.getElementById("search-notifications");
    const PLATFORM_FILTER = document.getElementById("platform-filter");
    const PRIORITY_FILTER = document.getElementById("priority-filter");

    // Fetch and render notifications
    const fetchNotifications = async (query = "", platform = "", priority = "") => {
        try {
            const url = new URL(NOTIFICATIONS_API_ENDPOINT, window.location.origin);
            url.searchParams.append("query", query);
            url.searchParams.append("platform", platform);
            url.searchParams.append("priority", priority);

            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch notifications");

            const data = await response.json();
            renderNotificationList(data.notifications);
        } catch (error) {
            console.error("Error fetching notifications:", error);
            NOTIFICATION_LIST_CONTAINER.innerHTML = `<p class="error-message">Error loading notifications. Please try again later.</p>`;
        }
    };

    // Render notification list in the DOM
    const renderNotificationList = (notifications) => {
        NOTIFICATION_LIST_CONTAINER.innerHTML = "";

        if (notifications.length === 0) {
            NOTIFICATION_LIST_CONTAINER.innerHTML = `<p>No notifications found for the selected filters or search.</p>`;
            return;
        }

        notifications.forEach((notification) => {
            const notificationItem = document.createElement("div");
            notificationItem.classList.add("notification-item");

            notificationItem.innerHTML = `
                <div class="notification-header">
                    <h3>${escapeHtml(notification.title)}</h3>
                    <span class="notification-priority ${notification.priority.toLowerCase()}">${notification.priority}</span>
                </div>
                <div class="notification-details">
                    <p><strong>Platform:</strong> ${escapeHtml(notification.platform)}</p>
                    <p><strong>Message:</strong> ${escapeHtml(notification.message)}</p>
                    <p><strong>Created:</strong> ${new Date(notification.createdAt).toLocaleString()}</p>
                </div>
                <div class="notification-actions">
                    <button class="edit-btn" data-id="${notification.id}">Edit</button>
                    <button class="delete-btn" data-id="${notification.id}">Delete</button>
                </div>
            `;

            // Attach event listeners to actions
            notificationItem.querySelector(".edit-btn").addEventListener("click", () => editNotification(notification.id));
            notificationItem.querySelector(".delete-btn").addEventListener("click", () => deleteNotification(notification.id));

            NOTIFICATION_LIST_CONTAINER.appendChild(notificationItem);
        });
    };

    // Add a new notification
    NOTIFICATION_FORM.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(NOTIFICATION_FORM);
        const notificationData = Object.fromEntries(formData.entries());

        try {
            const response = await fetch(NOTIFICATIONS_API_ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(notificationData)
            });

            if (!response.ok) throw new Error("Failed to add notification");

            fetchNotifications(); // Refresh the notification list
            NOTIFICATION_FORM.reset();
        } catch (error) {
            console.error("Error adding notification:", error);
            alert("Failed to add the notification. Please try again.");
        }
    });

    // Edit an existing notification
    const editNotification = async (notificationId) => {
        const notificationTitle = prompt("Enter new title for the notification:");
        if (!notificationTitle) return;

        try {
            const response = await fetch(`${NOTIFICATIONS_API_ENDPOINT}/${notificationId}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ title: notificationTitle })
            });

            if (!response.ok) throw new Error("Failed to edit notification");

            fetchNotifications(); // Refresh the notification list
        } catch (error) {
            console.error("Error editing notification:", error);
            alert("Failed to edit the notification. Please try again.");
        }
    };

    // Delete a notification
    const deleteNotification = async (notificationId) => {
        try {
            const response = await fetch(`${NOTIFICATIONS_API_ENDPOINT}/${notificationId}`, {
                method: "DELETE"
            });

            if (!response.ok) throw new Error("Failed to delete notification");

            fetchNotifications(); // Refresh the notification list
        } catch (error) {
            console.error("Error deleting notification:", error);
            alert("Failed to delete the notification. Please try again.");
        }
    };

    // Escape HTML for security
    const escapeHtml = (str) => {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    };

    // Search and filter functionality
    SEARCH_INPUT.addEventListener("input", () => {
        fetchNotifications(SEARCH_INPUT.value, PLATFORM_FILTER.value, PRIORITY_FILTER.value);
    });

    PLATFORM_FILTER.addEventListener("change", () => {
        fetchNotifications(SEARCH_INPUT.value, PLATFORM_FILTER.value, PRIORITY_FILTER.value);
    });

    PRIORITY_FILTER.addEventListener("change", () => {
        fetchNotifications(SEARCH_INPUT.value, PLATFORM_FILTER.value, PRIORITY_FILTER.value);
    });

    // Initial fetch of notifications
    fetchNotifications();
});
