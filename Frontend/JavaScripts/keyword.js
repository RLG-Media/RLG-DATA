// keyword.js

// DOM Elements
const keywordForm = document.getElementById("keyword-form");
const keywordInput = document.getElementById("keyword-input");
const resultTableBody = document.getElementById("result-table-body");
const chartContainer = document.getElementById("chart-container");
const loader = document.getElementById("loader");

// Constants
const API_URL = "/api/keywords";

// Utility Functions
const showLoader = () => {
    loader.style.display = "block";
};

const hideLoader = () => {
    loader.style.display = "none";
};

const displayError = (message) => {
    alert(`Error: ${message}`);
};

const clearResults = () => {
    resultTableBody.innerHTML = "";
    chartContainer.innerHTML = "";
};

// Fetch Data from Backend
const fetchKeywordData = async (keyword) => {
    showLoader();
    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ keyword }),
        });

        if (!response.ok) {
            throw new Error("Failed to fetch keyword data.");
        }

        const data = await response.json();
        hideLoader();
        return data;
    } catch (error) {
        hideLoader();
        displayError(error.message);
        return null;
    }
};

// Render Table Results
const renderTable = (results) => {
    clearResults();
    results.forEach((item) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.keyword}</td>
            <td>${item.searchVolume}</td>
            <td>${item.competition}</td>
            <td>${item.trendScore}</td>
        `;
        resultTableBody.appendChild(row);
    });
};

// Render Chart
const renderChart = (results) => {
    const keywords = results.map((item) => item.keyword);
    const volumes = results.map((item) => item.searchVolume);

    const canvas = document.createElement("canvas");
    chartContainer.appendChild(canvas);

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: keywords,
            datasets: [
                {
                    label: "Search Volume",
                    data: volumes,
                    backgroundColor: "rgba(75, 192, 192, 0.6)",
                    borderColor: "rgba(75, 192, 192, 1)",
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                },
            },
        },
    });
};

// Handle Form Submission
keywordForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const keyword = keywordInput.value.trim();
    if (!keyword) {
        displayError("Please enter a keyword.");
        return;
    }

    const data = await fetchKeywordData(keyword);
    if (data && data.results) {
        renderTable(data.results);
        renderChart(data.results);
    } else {
        displayError("No data available for the entered keyword.");
    }
});
