document.addEventListener("DOMContentLoaded", () => {
    // Constants for API endpoints and DOM elements
    const DATA_INSIGHTS_API = "/api/data-insights";
    const DASHBOARD_CONTAINER = document.getElementById("dashboard-container");
    const DATE_FILTER = document.getElementById("date-filter");
    const PLATFORM_FILTER = document.getElementById("platform-filter");
    const CATEGORY_FILTER = document.getElementById("category-filter");
    const EXPORT_BUTTON = document.getElementById("export-insights");
    const LOADER = document.getElementById("loader");

    // Fetch and render insights data
    const fetchInsights = async (dateRange = "", platform = "", category = "") => {
        try {
            showLoader();
            const url = new URL(DATA_INSIGHTS_API, window.location.origin);
            url.searchParams.append("dateRange", dateRange);
            url.searchParams.append("platform", platform);
            url.searchParams.append("category", category);

            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch data insights");

            const insightsData = await response.json();
            renderDashboard(insightsData);
        } catch (error) {
            console.error("Error fetching insights:", error);
            DASHBOARD_CONTAINER.innerHTML = `<p class="error-message">Error loading data insights. Please try again later.</p>`;
        } finally {
            hideLoader();
        }
    };

    // Render insights on the dashboard
    const renderDashboard = (insights) => {
        DASHBOARD_CONTAINER.innerHTML = "";

        if (!insights || insights.length === 0) {
            DASHBOARD_CONTAINER.innerHTML = `<p>No insights available for the selected filters.</p>`;
            return;
        }

        insights.forEach((insight) => {
            const insightCard = document.createElement("div");
            insightCard.classList.add("insight-card");

            insightCard.innerHTML = `
                <h3>${escapeHtml(insight.title)}</h3>
                <p><strong>Platform:</strong> ${escapeHtml(insight.platform)}</p>
                <p><strong>Category:</strong> ${escapeHtml(insight.category)}</p>
                <p><strong>Value:</strong> ${escapeHtml(insight.value)}</p>
                <p><strong>Last Updated:</strong> ${new Date(insight.lastUpdated).toLocaleString()}</p>
            `;

            DASHBOARD_CONTAINER.appendChild(insightCard);
        });
    };

    // Export insights data to a CSV file
    const exportInsights = async () => {
        try {
            const url = new URL(DATA_INSIGHTS_API + "/export", window.location.origin);
            const response = await fetch(url);

            if (!response.ok) throw new Error("Failed to export data insights");

            const blob = await response.blob();
            const downloadLink = document.createElement("a");
            downloadLink.href = URL.createObjectURL(blob);
            downloadLink.download = "data_insights.csv";
            downloadLink.click();
        } catch (error) {
            console.error("Error exporting insights:", error);
            alert("Failed to export insights. Please try again later.");
        }
    };

    // Show loader during data fetching
    const showLoader = () => {
        LOADER.style.display = "block";
    };

    // Hide loader after data fetching
    const hideLoader = () => {
        LOADER.style.display = "none";
    };

    // Escape HTML for security
    const escapeHtml = (str) => {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    };

    // Event listeners for filters and export button
    DATE_FILTER.addEventListener("change", () => {
        fetchInsights(DATE_FILTER.value, PLATFORM_FILTER.value, CATEGORY_FILTER.value);
    });

    PLATFORM_FILTER.addEventListener("change", () => {
        fetchInsights(DATE_FILTER.value, PLATFORM_FILTER.value, CATEGORY_FILTER.value);
    });

    CATEGORY_FILTER.addEventListener("change", () => {
        fetchInsights(DATE_FILTER.value, PLATFORM_FILTER.value, CATEGORY_FILTER.value);
    });

    EXPORT_BUTTON.addEventListener("click", exportInsights);

    // Initial fetch of data insights
    fetchInsights();
});
