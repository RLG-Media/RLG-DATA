document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatMessages = document.getElementById("chat-messages");

    // Function to append a message to the chat
    const appendMessage = (message, type) => {
        const messageDiv = document.createElement("div");
        messageDiv.textContent = message;
        messageDiv.className = type === "bot" ? "bot-message" : "user-message";
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Handle form submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (message) {
            appendMessage(message, "user");
            userInput.value = "";
            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ message: message, user_id: "12345" }),
                });
                const data = await response.json();
                appendMessage(data.response, "bot");
            } catch (error) {
                appendMessage("An error occurred. Please try again.", "bot");
            }
        }
    });
});
function toggleChat() {
    const chatPopup = document.getElementById("chat-popup");
    chatPopup.style.display =
        chatPopup.style.display === "none" ? "block" : "none";
}
