// google_business.js

document.addEventListener("DOMContentLoaded", () => {
    const accountsContainer = document.getElementById("accounts-container");
    const locationsContainer = document.getElementById("locations-container");
    const reviewsChart = document.getElementById("reviews-chart");
    const keywordsList = document.getElementById("keywords-list");
    const generateReportBtn = document.getElementById("generate-report-btn");
    const locationModal = document.getElementById("location-modal");
    const closeModalBtn = document.getElementById("close-modal-btn");
    const locationDetails = document.getElementById("location-details");

    let chartInstance = null;

    /**
     * Fetch Google Business Accounts from the Backend.
     */
    async function fetchAccounts() {
        try {
            const response = await fetch("/api/google_business/accounts");
            const data = await response.json();

            if (data.accounts && data.accounts.length > 0) {
                accountsContainer.innerHTML = data.accounts
                    .map(
                        (account) =>
                            `<div class="account-item" data-account-id="${account.id}">
                                <h3>${account.name}</h3>
                                <p>${account.email}</p>
                                <button class="btn-view-locations" data-account-id="${account.id}">View Locations</button>
                            </div>`
                    )
                    .join("");
                attachAccountListeners();
            } else {
                accountsContainer.innerHTML = "<p>No accounts found.</p>";
            }
        } catch (error) {
            accountsContainer.innerHTML = `<p>Error fetching accounts: ${error.message}</p>`;
        }
    }

    /**
     * Attach Event Listeners to Account Buttons.
     */
    function attachAccountListeners() {
        const locationButtons = document.querySelectorAll(".btn-view-locations");
        locationButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const accountId = button.dataset.accountId;
                fetchLocations(accountId);
            });
        });
    }

    /**
     * Fetch Locations for a Specific Account.
     */
    async function fetchLocations(accountId) {
        try {
            const response = await fetch(`/api/google_business/accounts/${accountId}/locations`);
            const data = await response.json();

            if (data.locations && data.locations.length > 0) {
                locationsContainer.innerHTML = data.locations
                    .map(
                        (location) =>
                            `<div class="location-item" data-location-id="${location.id}">
                                <h4>${location.name}</h4>
                                <p>${location.address}</p>
                                <button class="btn-view-details" data-location-id="${location.id}">View Details</button>
                            </div>`
                    )
                    .join("");
                attachLocationListeners();
            } else {
                locationsContainer.innerHTML = "<p>No locations found.</p>";
            }
        } catch (error) {
            locationsContainer.innerHTML = `<p>Error fetching locations: ${error.message}</p>`;
        }
    }

    /**
     * Attach Event Listeners to Location Buttons.
     */
    function attachLocationListeners() {
        const detailButtons = document.querySelectorAll(".btn-view-details");
        detailButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const locationId = button.dataset.locationId;
                fetchLocationDetails(locationId);
            });
        });
    }

    /**
     * Fetch and Display Location Details in Modal.
     */
    async function fetchLocationDetails(locationId) {
        try {
            const response = await fetch(`/api/google_business/locations/${locationId}`);
            const data = await response.json();

            locationDetails.innerHTML = `
                <h3>${data.name}</h3>
                <p>${data.address}</p>
                <p>Phone: ${data.phone}</p>
                <p>Status: ${data.status}</p>
                <p>Ratings: ${data.ratings.average} (${data.ratings.total} reviews)</p>
            `;
            locationModal.classList.remove("hidden");
        } catch (error) {
            locationDetails.innerHTML = `<p>Error fetching location details: ${error.message}</p>`;
        }
    }

    /**
     * Close Location Modal.
     */
    closeModalBtn.addEventListener("click", () => {
        locationModal.classList.add("hidden");
    });

    /**
     * Fetch and Render Reviews Analysis.
     */
    async function fetchReviewsAnalysis() {
        try {
            const response = await fetch("/api/google_business/reviews");
            const data = await response.json();

            if (chartInstance) chartInstance.destroy(); // Clear existing chart

            chartInstance = new Chart(reviewsChart, {
                type: "pie",
                data: {
                    labels: ["Positive", "Neutral", "Negative"],
                    datasets: [
                        {
                            data: [data.positive, data.neutral, data.negative],
                            backgroundColor: ["#4CAF50", "#FFC107", "#F44336"],
                        },
                    ],
                },
            });

            keywordsList.innerHTML = data.keywords
                .map((keyword) => `<li>${keyword}</li>`)
                .join("");
        } catch (error) {
            keywordsList.innerHTML = `<p>Error fetching reviews analysis: ${error.message}</p>`;
        }
    }

    /**
     * Generate a Report.
     */
    generateReportBtn.addEventListener("click", async () => {
        try {
            const response = await fetch("/api/google_business/report", {
                method: "POST",
            });
            const data = await response.json();

            if (data.report_url) {
                alert("Report generated successfully!");
                window.open(data.report_url, "_blank");
            } else {
                alert("Failed to generate report.");
            }
        } catch (error) {
            alert(`Error generating report: ${error.message}`);
        }
    });

    // Initial Load
    fetchAccounts();
    fetchReviewsAnalysis();
});
