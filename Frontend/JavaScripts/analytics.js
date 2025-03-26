// Analytics.js - Handles Analytics Features

// Document Ready
document.addEventListener("DOMContentLoaded", () => {
    initializeAnalytics();
    setupEventListeners();
    console.log("Analytics.js loaded successfully!");
});

// Global Variables
const analyticsDataUrl = "/api/analytics"; // Endpoint for fetching analytics data
let chartInstances = {}; // Stores Chart.js instances

// Initialize Analytics
function initializeAnalytics() {
    loadAnalyticsData();
}

// Load Analytics Data
function loadAnalyticsData() {
    fetch(analyticsDataUrl)
        .then((response) => response.json())
        .then((data) => {
            if (data && data.metrics && data.charts) {
                renderKeyMetrics(data.metrics);
                renderCharts(data.charts);
            } else {
                console.error("Invalid analytics data format.");
                showNotification("Failed to load analytics data.", "error");
            }
        })
        .catch((error) => {
            console.error("Error fetching analytics data:", error);
            showNotification("Error loading analytics data. Please try again.", "error");
        });
}

// Render Key Metrics
function renderKeyMetrics(metrics) {
    const metricsContainer = document.querySelector("#metrics-container");
    if (!metricsContainer) {
        console.warn("Metrics container not found.");
        return;
    }

    metricsContainer.innerHTML = ""; // Clear existing content
    metrics.forEach((metric) => {
        const metricCard = `
            <div class="metric-card">
                <h3>${metric.value}</h3>
                <p>${metric.label}</p>
            </div>
        `;
        metricsContainer.insertAdjacentHTML("beforeend", metricCard);
    });
}

// Render Charts
function renderCharts(chartData) {
    const chartContainer = document.querySelector("#chart-container");
    if (!chartContainer) {
        console.warn("Chart container not found.");
        return;
    }

    chartContainer.innerHTML = ""; // Clear existing charts
    chartData.forEach((chartInfo) => {
        const chartCanvas = document.createElement("canvas");
        chartCanvas.id = chartInfo.id;
        chartContainer.appendChild(chartCanvas);

        // Create Chart.js instance
        const ctx = chartCanvas.getContext("2d");
        const chart = new Chart(ctx, {
            type: chartInfo.type,
            data: chartInfo.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true },
                    tooltip: { enabled: true },
                },
                ...chartInfo.options, // Merge additional options
            },
        });

        // Store chart instance for future updates
        chartInstances[chartInfo.id] = chart;
    });
}

// Update Chart Data
function updateChartData(chartId, newData) {
    const chart = chartInstances[chartId];
    if (chart) {
        chart.data = newData;
        chart.update();
    } else {
        console.error(`Chart with ID "${chartId}" not found.`);
    }
}

// Event Listeners
function setupEventListeners() {
    const filterForm = document.querySelector("#filter-form");
    const dateRangePicker = document.querySelector("#date-range-picker");

    if (filterForm) {
        filterForm.addEventListener("submit", (event) => {
            event.preventDefault();
            const formData = new FormData(filterForm);
            applyFilters(Object.fromEntries(formData));
        });
    }

    if (dateRangePicker) {
        dateRangePicker.addEventListener("change", (event) => {
            const selectedRange = event.target.value;
            fetchFilteredAnalyticsData({ dateRange: selectedRange });
        });
    }
}

// Apply Filters
function applyFilters(filters) {
    console.log("Applying filters:", filters);
    fetchFilteredAnalyticsData(filters);
}

// Fetch Filtered Analytics Data
function fetchFilteredAnalyticsData(filters) {
    const queryParams = new URLSearchParams(filters).toString();
    const url = `${analyticsDataUrl}?${queryParams}`;

    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            if (data && data.metrics && data.charts) {
                renderKeyMetrics(data.metrics);
                data.charts.forEach((chart) => {
                    updateChartData(chart.id, chart.data);
                });
            } else {
                console.error("Invalid filtered analytics data format.");
                showNotification("Failed to load filtered data.", "error");
            }
        })
        .catch((error) => {
            console.error("Error fetching filtered analytics data:", error);
            showNotification("Error applying filters. Please try again.", "error");
        });
}

// Notification Utility
function showNotification(message, type = "success") {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Utility: Format Numbers
function formatNumber(num) {
    return num.toLocaleString("en-US");
}

// Utility: Generate Random Colors for Charts
function generateRandomColors(count) {
    return Array.from({ length: count }, () => {
        const randomColor = `rgba(${randomInt(0, 255)}, ${randomInt(0, 255)}, ${randomInt(0, 255)}, 0.7)`;
        return randomColor;
    });
}

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
