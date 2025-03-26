document.addEventListener("DOMContentLoaded", function () {
    const chatBody = document.getElementById("chat-body");
    const inputField = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const loader = document.getElementById("loader");
    const switchButton = document.getElementById("switch-dashboard");

    // Function to send user message
    function sendMessage() {
        const message = inputField.value.trim();
        if (message === "") return;

        appendMessage("user-message", message);
        inputField.value = "";
        loader.style.display = "block"; 

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                user_id: getUserID(), 
                location: getUserLocation()
            })
        })
        .then(response => response.json())
        .then(data => {
            loader.style.display = "none";
            appendMessage("bot-message", data.response);
        })
        .catch(error => {
            loader.style.display = "none";
            appendMessage("bot-message", "⚠️ Error: Unable to connect. Please try again.");
            console.error("Chatbot API error:", error);
        });
    }

    // Function to append messages
    function appendMessage(type, message) {
        let messageDiv = document.createElement("div");
        messageDiv.classList.add("chat-message", type);
        messageDiv.innerHTML = message;
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Function to get user ID (Stored Locally)
    function getUserID() {
        let userID = localStorage.getItem("user_id");
        if (!userID) {
            userID = "user_" + Math.random().toString(36).substr(2, 9);
            localStorage.setItem("user_id", userID);
        }
        return userID;
    }

    // Function to get user location (IP-based)
    function getUserLocation() {
        return fetch("https://ipapi.co/json/")
            .then(response => response.json())
            .then(data => ({
                country: data.country_name,
                city: data.city,
                region: data.region
            }))
            .catch(() => ({ country: "Unknown", city: "Unknown", region: "Unknown" }));
    }

    // Function to switch between dashboards
    function switchDashboard() {
        window.location.href = "/dashboard/fans";  
    }

    // Event Listeners
    sendButton.addEventListener("click", sendMessage);
    inputField.addEventListener("keypress", function (event) {
        if (event.key === "Enter") sendMessage();
    });
    switchButton.addEventListener("click", switchDashboard);
});
