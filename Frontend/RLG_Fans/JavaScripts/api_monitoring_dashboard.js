document.addEventListener("DOMContentLoaded", function () {
    const apiStatusTable = document.getElementById("api-status-table");
    const refreshButton = document.getElementById("refresh-api-status");
    const apiStatsChart = document.getElementById("api-stats-chart").getContext("2d");

    let apiChart;

    // Fetch API status
    async function fetchAPIStatus() {
        try {
            const response = await fetch("/api/monitoring/status");
            const data = await response.json();
            updateAPITable(data);
            updateAPIChart(data);
        } catch (error) {
            console.error("Error fetching API status:", error);
            alert("Failed to fetch API status. Please check your connection.");
        }
    }

    // Update API Status Table
    function updateAPITable(data) {
        apiStatusTable.innerHTML = "";
        data.forEach(api => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${api.name}</td>
                <td>${api.status === "online" ? "🟢 Online" : "🔴 Offline"}</td>
                <td>${api.responseTime} ms</td>
                <td>${api.errorRate}%</td>
                <td>${new Date(api.lastChecked).toLocaleString()}</td>
            `;
            apiStatusTable.appendChild(row);
        });
    }

    // Update API Statistics Chart
    function updateAPIChart(data) {
        const labels = data.map(api => api.name);
        const responseTimes = data.map(api => api.responseTime);
        const errorRates = data.map(api => api.errorRate);

        if (apiChart) apiChart.destroy();

        apiChart = new Chart(apiStatsChart, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Response Time (ms)",
                        data: responseTimes,
                        backgroundColor: "rgba(54, 162, 235, 0.6)",
                    },
                    {
                        label: "Error Rate (%)",
                        data: errorRates,
                        backgroundColor: "rgba(255, 99, 132, 0.6)",
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // Refresh API Status
    refreshButton.addEventListener("click", fetchAPIStatus);

    // Auto Refresh every 60 seconds
    setInterval(fetchAPIStatus, 60000);

    // Initial Load
    fetchAPIStatus();
});
