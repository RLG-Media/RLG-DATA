// service_health_dashboard.js

// Global variables for tracking service health
const services = [
    {
        name: "RLG Data API",
        url: "/api/health/data",
        type: "API"
    },
    {
        name: "RLG Fans API",
        url: "/api/health/fans",
        type: "API"
    },
    {
        name: "Social Media Integration - Facebook",
        url: "/api/health/facebook",
        type: "Integration"
    },
    {
        name: "Social Media Integration - Twitter",
        url: "/api/health/twitter",
        type: "Integration"
    },
    {
        name: "Social Media Integration - Instagram",
        url: "/api/health/instagram",
        type: "Integration"
    },
    {
        name: "Social Media Integration - LinkedIn",
        url: "/api/health/linkedin",
        type: "Integration"
    }
    // Add more services as needed
];

// DOM elements
const dashboardTable = document.getElementById("service-health-table");
const lastUpdated = document.getElementById("last-updated");

// Utility to format the current timestamp
const formatTimestamp = () => {
    const now = new Date();
    return now.toLocaleString();
};

// Utility to update last updated time
const updateLastUpdated = () => {
    lastUpdated.textContent = `Last updated: ${formatTimestamp()}`;
};

// Render service health status
const renderServiceHealth = (statuses) => {
    dashboardTable.innerHTML = ""; // Clear table

    statuses.forEach((status) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${status.name}</td>
            <td>${status.type}</td>
            <td class="status ${status.status.toLowerCase()}">${status.status}</td>
            <td>${status.responseTime}ms</td>
        `;

        dashboardTable.appendChild(row);
    });
};

// Fetch service health
const fetchServiceHealth = async () => {
    const statuses = await Promise.all(
        services.map(async (service) => {
            const startTime = performance.now();
            try {
                const response = await fetch(service.url);
                const responseTime = Math.round(performance.now() - startTime);

                if (response.ok) {
                    return {
                        name: service.name,
                        type: service.type,
                        status: "Healthy",
                        responseTime
                    };
                } else {
                    return {
                        name: service.name,
                        type: service.type,
                        status: "Unhealthy",
                        responseTime
                    };
                }
            } catch (error) {
                return {
                    name: service.name,
                    type: service.type,
                    status: "Offline",
                    responseTime: "N/A"
                };
            }
        })
    );

    renderServiceHealth(statuses);
    updateLastUpdated();
};

// Polling interval for real-time updates
const POLLING_INTERVAL = 60000; // 1 minute

// Start polling service health
const startPolling = () => {
    fetchServiceHealth(); // Initial fetch
    setInterval(fetchServiceHealth, POLLING_INTERVAL);
};

// Initialize the dashboard
window.addEventListener("DOMContentLoaded", () => {
    startPolling();
});
