document.addEventListener("DOMContentLoaded", async () => {
    // Global variables
    const trendingContainer = document.getElementById("trendingContent");
    const searchInput = document.getElementById("trendSearch");
    const filterPlatform = document.getElementById("filterPlatform");
    const filterRegion = document.getElementById("filterRegion");
    const chartCanvas = document.getElementById("trendChart").getContext("2d");
    let trendChart;

    // Fetch trending insights from API
    async function fetchTrendingInsights(platform, region, query = "") {
        try {
            const response = await fetch(`/api/trends?platform=${platform}&region=${region}&query=${query}`);
            const data = await response.json();
            renderTrendingContent(data);
            updateChart(data);
        } catch (error) {
            console.error("Error fetching trending insights:", error);
            trendingContainer.innerHTML = `<p class="error">Failed to load trends. Please try again.</p>`;
        }
    }

    // Render trending content dynamically
    function renderTrendingContent(trends) {
        trendingContainer.innerHTML = "";
        trends.forEach((trend) => {
            const trendItem = document.createElement("div");
            trendItem.className = "trend-item";
            trendItem.innerHTML = `
                <h4>${escapeHtml(trend.title)}</h4>
                <p>${escapeHtml(trend.description)}</p>
                <span class="platform-tag">${trend.platform}</span>
                <span class="region-tag">${trend.region}</span>
                <span class="sentiment ${getSentimentClass(trend.sentiment)}">
                    ${trend.sentiment_score} Sentiment
                </span>
            `;
            trendingContainer.appendChild(trendItem);
        });
    }

    // Update Chart with trend data
    function updateChart(trends) {
        const labels = trends.map(trend => trend.title);
        const dataValues = trends.map(trend => trend.popularity_score);

        if (trendChart) {
            trendChart.destroy();
        }

        trendChart = new Chart(chartCanvas, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Popularity Score",
                    data: dataValues,
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    borderColor: "rgba(75, 192, 192, 1)",
                    borderWidth: 1
                }]
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

    // Escape HTML for security
    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // Assign sentiment class
    function getSentimentClass(score) {
        return score > 0.6 ? "positive" : score < 0.4 ? "negative" : "neutral";
    }

    // Handle search and filter changes
    searchInput.addEventListener("input", () => {
        fetchTrendingInsights(filterPlatform.value, filterRegion.value, searchInput.value);
    });

    filterPlatform.addEventListener("change", () => {
        fetchTrendingInsights(filterPlatform.value, filterRegion.value, searchInput.value);
    });

    filterRegion.addEventListener("change", () => {
        fetchTrendingInsights(filterPlatform.value, filterRegion.value, searchInput.value);
    });

    // Load initial trends on page load
    fetchTrendingInsights("all", "global", "");
});
