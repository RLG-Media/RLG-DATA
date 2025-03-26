// wordcloud.js - Handles rendering and interactivity for the word cloud

document.addEventListener("DOMContentLoaded", () => {
    initializeWordCloud();
    console.log("WordCloud.js loaded successfully!");
});

// Global Variables
const wordCloudContainer = document.getElementById("word-cloud-container"); // Word cloud container
const wordCloudApiUrl = "/api/wordcloud"; // Endpoint to fetch word cloud data

// Initialize Word Cloud
function initializeWordCloud() {
    if (!wordCloudContainer) {
        console.warn("Word cloud container not found.");
        return;
    }

    fetchWordCloudData()
        .then((wordData) => {
            renderWordCloud(wordData);
        })
        .catch((error) => {
            console.error("Error initializing word cloud:", error);
            showNotification("Failed to load word cloud. Please try again.", "error");
        });
}

// Fetch Word Cloud Data from API
async function fetchWordCloudData() {
    try {
        const response = await fetch(wordCloudApiUrl);
        if (!response.ok) {
            throw new Error(`Failed to fetch word cloud data. Status: ${response.status}`);
        }

        const data = await response.json();
        if (!Array.isArray(data.words)) {
            throw new Error("Invalid word cloud data format.");
        }

        return data.words.map((word) => [word.text, word.weight]);
    } catch (error) {
        console.error("Error fetching word cloud data:", error);
        throw error;
    }
}

// Render Word Cloud
function renderWordCloud(wordData) {
    WordCloud(wordCloudContainer, {
        list: wordData,
        gridSize: Math.round(16 * wordCloudContainer.offsetWidth / 1024),
        weightFactor: 10,
        fontFamily: "Arial, sans-serif",
        color: (word, weight) => getRandomColor(),
        rotateRatio: 0.5,
        rotationSteps: 2,
        backgroundColor: "#f8f9fa",
        click: handleWordClick
    });

    console.log("Word cloud rendered successfully!");
}

// Handle Word Click Event
function handleWordClick(word, weight, event) {
    const message = `You clicked on "${word}" with a weight of ${weight}.`;
    console.log(message);
    showNotification(message, "info");
}

// Generate Random Colors for Word Cloud
function getRandomColor() {
    const colors = ["#007bff", "#28a745", "#dc3545", "#ffc107", "#6c757d", "#17a2b8"];
    return colors[Math.floor(Math.random() * colors.length)];
}

// Utility: Show Notifications
function showNotification(message, type = "info") {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
