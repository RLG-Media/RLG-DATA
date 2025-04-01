/**
 * pricing_page.js
 *
 * This script dynamically loads and displays the pricing tiers for RLG Data & RLG Fans
 * based on the user's locked location. It applies:
 *  - Special Region pricing for Israel (hard locked so that Israeli users cannot change their location),
 *  - SADC region pricing for select African countries, and
 *  - Default global pricing for all other regions.
 *
 * The pricing data is fetched from a backend API endpoint (/api/pricing). Once the user's
 * pricing is determined (after registration), the UI is updated accordingly.
 *
 * Additional functionalities:
 *  - Disables location selection for users in special regions.
 *  - Displays a friendly region-based welcome banner.
 *  - Provides error handling and logs issues to the console.
 *
 * Note: Ensure that the backend is configured to lock pricing based on user registration and location.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Fetch pricing data from the backend API once the DOM is ready.
    fetchPricingData();

    /**
     * Fetch pricing data from the backend.
     */
    function fetchPricingData() {
        // Replace '/api/pricing' with your actual API endpoint.
        fetch("/api/pricing")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                console.log("Pricing data received:", data);
                updatePricingUI(data);
                updateRegionBanner(data);
            })
            .catch(error => {
                console.error("Error fetching pricing data:", error);
                alert("Unable to load pricing data. Please try again later.");
            });
    }

    /**
     * Updates the pricing container based on the retrieved pricing data.
     *
     * @param {Object} data - The pricing data from the backend, expected to include:
     *                        - user_id, location (with country), pricing_option, price, and currency.
     */
    function updatePricingUI(data) {
        const priceContainer = document.getElementById("pricing-container");
        if (!priceContainer) return;

        let pricingHTML = "";

        // Determine pricing display based on user's location.
        // Expecting 'data.location.country' to be provided.
        if (data.location && data.location.country === "Israel") {
            pricingHTML += `<h3>Special Region Pricing (Israel):</h3>`;
            pricingHTML += `<p>CREATOR: $99 Monthly / $35 Weekly</p>`;
            pricingHTML += `<p>PRO: $499 Monthly / $99 Weekly</p>`;
            pricingHTML += `<p>ENTERPRISE: $699 Monthly</p>`;
            pricingHTML += `<p>RLG Media Pack: $2500 Monthly</p>`;
            disableLocationChange();
        } else if (isSADCRegion(data.location.country)) {
            pricingHTML += `<h3>Africa & SADC Region Pricing:</h3>`;
            pricingHTML += `<p>CREATOR: $30 Monthly / $8 Weekly</p>`;
            pricingHTML += `<p>PRO: $59 Monthly / $15 Weekly</p>`;
            pricingHTML += `<p>ENTERPRISE: $299 Monthly</p>`;
            pricingHTML += `<p>RLG Media Pack: $1500 Monthly</p>`;
        } else {
            pricingHTML += `<h3>Global Pricing:</h3>`;
            pricingHTML += `<p>CREATOR: $59 Monthly / $15 Weekly</p>`;
            pricingHTML += `<p>PRO: $99 Monthly / $35 Weekly</p>`;
            pricingHTML += `<p>ENTERPRISE: $299 Monthly</p>`;
            pricingHTML += `<p>RLG Media Pack: $1500 Monthly</p>`;
        }

        priceContainer.innerHTML = pricingHTML;
    }

    /**
     * Checks if the given country belongs to the SADC region.
     *
     * @param {string} country - The full country name.
     * @returns {boolean} True if the country is in the SADC region, false otherwise.
     */
    function isSADCRegion(country) {
        if (!country) return false;
        const sadcCountries = [
            "South Africa", "Botswana", "Namibia", "Zimbabwe", "Mozambique",
            "Zambia", "Malawi", "Lesotho", "Eswatini", "Angola", "Democratic Republic of Congo",
            "Tanzania"
        ];
        return sadcCountries.some(c => c.toLowerCase() === country.toLowerCase());
    }

    /**
     * Updates the region banner with a friendly greeting based on the user's detected location.
     *
     * @param {Object} data - The pricing data containing location information.
     */
    function updateRegionBanner(data) {
        const regionBanner = document.getElementById("region-banner");
        if (regionBanner && data.location) {
            regionBanner.textContent = `Welcome from ${data.location.city}, ${data.location.country}!`;
        }
    }

    /**
     * Disables the location selection control to lock the user's location.
     * This prevents users in a Special Region (e.g., Israel) from changing their location.
     */
    function disableLocationChange() {
        const locationSelect = document.getElementById("location-select");
        if (locationSelect) {
            locationSelect.disabled = true;
            let warningMessage = document.createElement("p");
            warningMessage.textContent = "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד.";
            warningMessage.className = "warning-message";
            locationSelect.parentElement.appendChild(warningMessage);
        }
    }
});
