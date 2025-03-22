document.addEventListener("DOMContentLoaded", () => {
    // Constants for API endpoints and heatmap configurations
    const API_USAGE_ENDPOINT = "/api/usage/data"; // Replace with your actual endpoint
    const HEATMAP_CONTAINER = document.getElementById("heatmap-container");

    // Initialize the heatmap
    const initHeatmap = () => {
        const heatmapInstance = h337.create({
            container: HEATMAP_CONTAINER,
            radius: 50,
            maxOpacity: 0.8,
            minOpacity: 0.2,
            blur: 0.75,
        });

        fetchHeatmapData(heatmapInstance);
    };

    // Fetch API usage data and populate heatmap
    const fetchHeatmapData = async (heatmapInstance) => {
        try {
            const response = await fetch(API_USAGE_ENDPOINT);
            if (!response.ok) {
                throw new Error(`Failed to fetch API usage data: ${response.statusText}`);
            }

            const usageData = await response.json();
            const heatmapData = formatHeatmapData(usageData);

            heatmapInstance.setData(heatmapData);
            displayUsageSummary(usageData);
        } catch (error) {
            console.error("Error fetching or processing API usage data:", error);
            HEATMAP_CONTAINER.innerHTML = `
                <p class="error-message">Error loading heatmap data. Please try again later.</p>`;
        }
    };

    // Format data for heatmap consumption
    const formatHeatmapData = (data) => {
        const points = data.map((entry) => ({
            x: entry.xCoordinate,
            y: entry.yCoordinate,
            value: entry.usageCount,
        }));

        return {
            max: Math.max(...data.map((entry) => entry.usageCount)),
            min: Math.min(...data.map((entry) => entry.usageCount)),
            data: points,
        };
    };

    // Display usage summary for better insights
    const displayUsageSummary = (data) => {
        const totalRequests = data.reduce((sum, entry) => sum + entry.usageCount, 0);
        const highestUsage = Math.max(...data.map((entry) => entry.usageCount));
        const lowestUsage = Math.min(...data.map((entry) => entry.usageCount));

        const summaryContainer = document.getElementById("usage-summary");
        summaryContainer.innerHTML = `
            <div class="summary-item">
                <h4>Total API Requests:</h4>
                <p>${totalRequests.toLocaleString()}</p>
            </div>
            <div class="summary-item">
                <h4>Highest Requests in a Region:</h4>
                <p>${highestUsage.toLocaleString()}</p>
            </div>
            <div class="summary-item">
                <h4>Lowest Requests in a Region:</h4>
                <p>${lowestUsage.toLocaleString()}</p>
            </div>`;
    };

    // Add filter functionality
    const applyFilters = () => {
        const filterRegion = document.getElementById("region-filter").value;
        const filterDateRange = document.getElementById("date-range-filter").value;

        fetch(`${API_USAGE_ENDPOINT}?region=${filterRegion}&dateRange=${filterDateRange}`)
            .then((response) => response.json())
            .then((filteredData) => {
                const heatmapInstance = h337.create({ container: HEATMAP_CONTAINER });
                const heatmapData = formatHeatmapData(filteredData);
                heatmapInstance.setData(heatmapData);
                displayUsageSummary(filteredData);
            })
            .catch((error) => {
                console.error("Error applying filters to heatmap:", error);
            });
    };

    // Attach event listener to filters
    document.getElementById("apply-filters").addEventListener("click", applyFilters);

    // Initialize heatmap on page load
    initHeatmap();
});
