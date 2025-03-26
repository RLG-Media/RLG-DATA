document.addEventListener("DOMContentLoaded", () => {
    const messageList = document.querySelector(".messages");
    const messageView = document.querySelector(".message-view");
    const searchInput = document.querySelector(".search-bar input");
    const actions = {
        markRead: document.querySelector(".actions button[title='Mark as Read']"),
        delete: document.querySelector(".actions button[title='Delete']"),
        refresh: document.querySelector(".actions button[title='Refresh']")
    };

    const loadMessages = async () => {
        try {
            const response = await fetch("/api/messages");
            const messages = await response.json();
            renderMessages(messages);
        } catch (error) {
            console.error("Failed to load messages:", error);
            messageList.innerHTML = `<p class="error">Error loading messages. Please try again later.</p>`;
        }
    };

    const renderMessages = (messages) => {
        messageList.innerHTML = "";
        messages.forEach((message) => {
            const messageItem = document.createElement("li");
            messageItem.className = `message ${message.read ? "" : "unread"}`;
            messageItem.innerHTML = `
                <input type="checkbox" data-id="${message.id}">
                <div class="message-info">
                    <h4 class="sender">${escapeHtml(message.sender)}</h4>
                    <p class="preview">${escapeHtml(message.preview)}</p>
                </div>
                <div class="message-meta">
                    <span class="timestamp">${formatTimestamp(message.timestamp)}</span>
                </div>
            `;
            messageItem.addEventListener("click", () => viewMessage(message));
            messageList.appendChild(messageItem);
        });
    };

    const viewMessage = async (message) => {
        try {
            const response = await fetch(`/api/messages/${message.id}`);
            const fullMessage = await response.json();
            messageView.innerHTML = `
                <h2>${escapeHtml(fullMessage.subject)}</h2>
                <p><strong>From:</strong> ${escapeHtml(fullMessage.sender)}</p>
                <p><strong>Received:</strong> ${formatTimestamp(fullMessage.timestamp)}</p>
                <div class="message-content">${escapeHtml(fullMessage.content)}</div>
            `;
            markMessageAsRead(message.id);
        } catch (error) {
            console.error("Failed to load message details:", error);
            messageView.innerHTML = `<p class="error">Error loading message. Please try again later.</p>`;
        }
    };

    const markMessageAsRead = async (id) => {
        try {
            await fetch(`/api/messages/${id}/mark-read`, { method: "POST" });
            document.querySelector(`input[data-id="${id}"]`).closest(".message").classList.remove("unread");
        } catch (error) {
            console.error("Failed to mark message as read:", error);
        }
    };

    const deleteMessages = async () => {
        const selected = Array.from(document.querySelectorAll(".messages input:checked"));
        if (selected.length === 0) {
            alert("Please select messages to delete.");
            return;
        }

        const ids = selected.map(input => input.dataset.id);
        try {
            await Promise.all(ids.map(id => fetch(`/api/messages/${id}`, { method: "DELETE" })));
            loadMessages();
            messageView.innerHTML = `<p>Select a message to view its content.</p>`;
        } catch (error) {
            console.error("Failed to delete messages:", error);
            alert("Error deleting messages. Please try again later.");
        }
    };

    const refreshInbox = () => {
        loadMessages();
        messageView.innerHTML = `<p>Select a message to view its content.</p>`;
    };

    const searchMessages = () => {
        const query = searchInput.value.toLowerCase();
        const messages = document.querySelectorAll(".messages .message");
        messages.forEach((message) => {
            const sender = message.querySelector(".sender").textContent.toLowerCase();
            const preview = message.querySelector(".preview").textContent.toLowerCase();
            message.style.display = sender.includes(query) || preview.includes(query) ? "" : "none";
        });
    };

    const escapeHtml = (str) => {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    };

    const formatTimestamp = (timestamp) => {
        return new Date(timestamp).toLocaleString();
    };

    searchInput.addEventListener("input", searchMessages);
    actions.markRead.addEventListener("click", () => {
        document.querySelectorAll(".messages input:checked").forEach((input) => {
            markMessageAsRead(input.dataset.id);
        });
    });
    actions.delete.addEventListener("click", deleteMessages);
    actions.refresh.addEventListener("click", refreshInbox);

    loadMessages();
});
