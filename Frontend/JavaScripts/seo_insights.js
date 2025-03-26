// Ensure the DOM is fully loaded before running scripts
document.addEventListener("DOMContentLoaded", () => {
    const keywordForm = document.getElementById("keyword-form");
    const searchVolumeTable = document.getElementById("search-volume-data");
    const competitorsTable = document.getElementById("competitors-data");
    const keywordStrengthList = document.getElementById("keyword-strength-data");
    const trendsList = document.getElementById("trends-data");

    const backendUrl = "http://localhost:5000/seo_insights"; // Update with your backend URL

    // Utility function to clear previous results
    function clearPreviousResults() {
        searchVolumeTable.innerHTML = "";
        competitorsTable.innerHTML = "";
        keywordStrengthList.innerHTML = "";
        trendsList.innerHTML = "";
    }

    // Utility function to create table rows
    function createTableRow(dataArray) {
        const row = document.createElement("tr");
        dataArray.forEach(data => {
            const cell = document.createElement("td");
            cell.textContent = data;
            row.appendChild(cell);
        });
        return row;
    }

    // Fetch and display search volume data
    function displaySearchVolume(data) {
        const row = createTableRow([
            data.keyword,
            data.total_results,
            data.search_time,
            data.featured_snippets ? "Yes" : "No",
        ]);
        searchVolumeTable.appendChild(row);
    }

    // Fetch and display competitors data
    function displayCompetitors(competitors) {
        competitors.forEach(comp => {
            const row = createTableRow([
                comp.rank,
                comp.title,
                comp.snippet,
                comp.link,
            ]);
            competitorsTable.appendChild(row);
        });
    }

    // Fetch and display keyword strength data
    function displayKeywordStrength(data) {
        const metrics = [
            `Keyword: ${data.keyword}`,
            `Total Results: ${data.total_results}`,
            `Competition Level: ${data.competition_level}`,
            `Has Featured Snippets: ${data.has_featured_snippets ? "Yes" : "No"}`,
        ];
        metrics.forEach(metric => {
            const listItem = document.createElement("li");
            listItem.textContent = metric;
            keywordStrengthList.appendChild(listItem);
        });
    }

    // Fetch and display related trends
    function displayTrends(trends) {
        trends.forEach(trend => {
            const listItem = document.createElement("li");
            listItem.textContent = `${trend.query} (Search Score: ${trend.search_score || "N/A"})`;
            trendsList.appendChild(listItem);
        });
    }

    // Handle form submission
    keywordForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const keyword = document.getElementById("keyword").value.trim();

        if (!keyword) {
            alert("Please enter a keyword to analyze.");
            return;
        }

        // Clear previous results
        clearPreviousResults();

        // Fetch data from backend
        try {
            const response = await fetch(`${backendUrl}?keyword=${encodeURIComponent(keyword)}`);
            if (!response.ok) {
                throw new Error("Failed to fetch data from the server.");
            }
            const result = await response.json();

            // Display data
            displaySearchVolume(result.search_volume);
            displayCompetitors(result.competitors);
            displayKeywordStrength(result.keyword_strength);
            displayTrends(result.related_trends);

        } catch (error) {
            console.error("Error fetching SEO insights:", error);
            alert("An error occurred while fetching SEO insights. Please try again.");
        }
    });
});
