/**
 * geolocation_service.js
 *
 * This script handles user location detection using ipapi.co and applies region-based pricing for RLG Data & RLG Fans.
 * It updates the UI (pricing, banners, hidden fields) and sends location data to the backend.
 *
 * Special Features:
 *  - Hard-locked "Special Region" pricing for Israel.
 *  - SADC region pricing for select African countries.
 *  - Default global pricing for all other regions.
 *  - Pricing page is accessible only after registration, locking the user's location.
 *  - Users in Israel cannot change their location for better pricing.
 *
 * Enhancements & Recommendations:
 *  - Improved error handling and logging.
 *  - Further integration with scraping and compliance tools can be added as needed.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize geolocation detection when the DOM is ready.
    initGeolocation();

    /**
     * Initializes the geolocation process by calling ipapi.co.
     */
    function initGeolocation() {
        fetch('https://ipapi.co/json/')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Geolocation failed:', data.error);
                    alert('Unable to detect location. Please try again.');
                } else {
                    handleGeolocationSuccess(data);
                }
            })
            .catch(error => {
                console.error('Error fetching geolocation:', error);
                alert('Unable to detect location. Please try again.');
            });
    }

    /**
     * Handles a successful geolocation response by:
     *  - Building a user location object.
     *  - Applying appropriate pricing rules based on region:
     *      - Israel: Special Region pricing (hard-locked).
     *      - SADC: Specific pricing tiers.
     *      - Default: Global pricing.
     *  - Updating hidden form fields and region banner.
     *  - Sending location data to the backend.
     *
     * @param {Object} data - Geolocation data from ipapi.co.
     */
    function handleGeolocationSuccess(data) {
        const userLocation = {
            country: data.country_name,      // e.g., "Israel"
            countryCode: data.country_code,    // e.g., "IL"
            region: data.region,               // e.g., "Tel Aviv District"
            city: data.city,                   // e.g., "Tel Aviv"
            ip: data.ip                       // Detected IP address
        };

        console.log('User location detected:', userLocation);

        // Apply pricing based on region:
        if (userLocation.countryCode === 'IL') {
            setPricingForIsrael();
        } else if (isUserInSADCRegion(userLocation.country)) {
            setPricingForSADC();
        } else {
            setDefaultPricing();
        }

        // Update hidden form fields
        const countryField = document.getElementById('user-country');
        const countryCodeField = document.getElementById('user-country-code');
        if (countryField) countryField.value = userLocation.country;
        if (countryCodeField) countryCodeField.value = userLocation.countryCode;

        // Update region banner with a greeting
        setRegionBanner(userLocation);

        // Send location data to the backend for further processing
        sendLocationToBackend(userLocation);
    }

    /**
     * Checks if a given country name (case-insensitive) is in the SADC region.
     *
     * @param {string} countryName - The full country name.
     * @returns {boolean} True if the country is in SADC, false otherwise.
     */
    function isUserInSADCRegion(countryName) {
        const sadcCountries = [
            "South Africa", "Botswana", "Namibia", "Zimbabwe",
            "Mozambique", "Zambia", "Malawi", "Lesotho", "Eswatini",
            "Angola", "Democratic Republic of Congo", "Tanzania"
        ];
        return sadcCountries.some(c => c.toLowerCase() === countryName.toLowerCase());
    }

    /**
     * Sets the pricing for users in Israel (Special Region) and disables location changes.
     */
    function setPricingForIsrael() {
        const priceContainer = document.getElementById('pricing');
        if (priceContainer) {
            priceContainer.innerHTML = '';
            // Special pricing tiers for Israel
            const pricingTiers = {
                "Creator": { weekly: 35, monthly: 99 },
                "Pro": { weekly: 99, monthly: 499 },
                "Enterprise": { weekly: "N/A", monthly: 699 },
                "RLG Media Pack": { weekly: "N/A", monthly: 2500 }
            };
            Object.entries(pricingTiers).forEach(([tier, prices]) => {
                const p = document.createElement('p');
                p.textContent = `${tier} - Weekly: ${prices.weekly !== "N/A" ? "$" + prices.weekly : "N/A"}, Monthly: $${prices.monthly}`;
                priceContainer.appendChild(p);
            });
        }
        disableLocationChange();
    }

    /**
     * Sets the pricing for users in SADC regions.
     */
    function setPricingForSADC() {
        const priceContainer = document.getElementById('pricing');
        if (priceContainer) {
            priceContainer.innerHTML = '';
            // SADC pricing tiers
            const pricingTiers = {
                "Creator": { weekly: 8, monthly: 30 },
                "Pro": { weekly: 15, monthly: 59 },
                "Enterprise": { weekly: "N/A", monthly: 299 },
                "RLG Media Pack": { weekly: "N/A", monthly: 1500 }
            };
            Object.entries(pricingTiers).forEach(([tier, prices]) => {
                const p = document.createElement('p');
                p.textContent = `${tier} - Weekly: ${prices.weekly !== "N/A" ? "$" + prices.weekly : "N/A"}, Monthly: $${prices.monthly}`;
                priceContainer.appendChild(p);
            });
        }
    }

    /**
     * Sets the default global pricing for users not in Israel or SADC.
     */
    function setDefaultPricing() {
        const priceContainer = document.getElementById('pricing');
        if (priceContainer) {
            priceContainer.innerHTML = '';
            // Default pricing tiers
            const pricingTiers = {
                "Creator": { weekly: 15, monthly: 59 },
                "Pro": { weekly: 35, monthly: 99 },
                "Enterprise": { weekly: "N/A", monthly: 299 },
                "RLG Media Pack": { weekly: "N/A", monthly: 2000 }
            };
            Object.entries(pricingTiers).forEach(([tier, prices]) => {
                const p = document.createElement('p');
                p.textContent = `${tier} - Weekly: ${prices.weekly !== "N/A" ? "$" + prices.weekly : "N/A"}, Monthly: $${prices.monthly}`;
                priceContainer.appendChild(p);
            });
        }
    }

    /**
     * Disables the location selection control so that users in a Special Region (Israel) cannot change their location.
     */
    function disableLocationChange() {
        const locationSelect = document.getElementById('location-select');
        if (locationSelect) {
            locationSelect.disabled = true;
            const warning = document.createElement('p');
            warning.textContent = 'Your location is locked to Israel and cannot be changed.';
            warning.classList.add('warning-message');
            locationSelect.parentElement.appendChild(warning);
        }
    }

    /**
     * Updates the region banner with a friendly greeting using the user's city and country.
     *
     * @param {Object} userLocation - The detected user location.
     */
    function setRegionBanner(userLocation) {
        const regionBanner = document.getElementById('region-banner');
        if (regionBanner) {
            regionBanner.textContent = `Welcome from ${userLocation.city}, ${userLocation.country}!`;
        }
    }

    /**
     * Sends the user location data to the backend for further processing (e.g., locking pricing, logging).
     *
     * @param {Object} locationData - The user location data object.
     */
    function sendLocationToBackend(locationData) {
        fetch('/update-location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
                // Include CSRF token if needed.
            },
            body: JSON.stringify(locationData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Location data sent to backend:', data);
        })
        .catch(error => {
            console.error('Error sending location to backend:', error);
        });
    }
});
