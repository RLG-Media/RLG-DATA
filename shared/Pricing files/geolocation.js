/**
 * geolocation.js
 *
 * This script handles the detection of user location based on IP using ipapi.co,
 * updates pricing and region settings dynamically for both RLG Data and RLG Fans,
 * and sends the detected location to the backend.
 *
 * Features:
 *  - Fetches user geolocation data via ipapi.co API.
 *  - Updates UI elements such as hidden input fields and banners.
 *  - Dynamically sets pricing tiers based on location (special handling for Israel).
 *  - Sends the user's location data to the backend for further processing.
 *
 * Recommendations:
 *  1. Consider enhancing error handling and user notifications.
 *  2. For more granular location accuracy (city/town), further processing or an alternative API may be used.
 *  3. Ensure that backend endpoints (like /update-location) are secured and handle CSRF tokens if needed.
 *  4. Customize the pricing tiers and UI messages to match your branding and requirements.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize geolocation detection when the DOM is ready.
    initGeolocation();

    /**
     * Initializes the geolocation process by calling the external API.
     */
    function initGeolocation() {
        // Use ipapi.co to fetch JSON geolocation data
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
     * Handles a successful geolocation response.
     * Updates the UI and applies pricing rules based on location.
     *
     * @param {Object} data - The geolocation data returned by ipapi.co.
     */
    function handleGeolocationSuccess(data) {
        // Build a user location object with key details.
        const userLocation = {
            country: data.country_name,       // e.g., "Israel"
            countryCode: data.country_code,     // e.g., "IL"
            region: data.region,                // e.g., "Tel Aviv District"
            city: data.city,                    // e.g., "Tel Aviv"
            ip: data.ip                         // Detected IP address
        };

        console.log('User location detected:', userLocation);

        // Apply pricing rules based on country code.
        if (userLocation.countryCode === 'IL') {
            setPricingForIsrael();
        } else {
            setDefaultPricing();
        }

        // Update hidden form fields with user location information.
        const countryField = document.getElementById('user-country');
        const countryCodeField = document.getElementById('user-country-code');
        if (countryField) countryField.value = userLocation.country;
        if (countryCodeField) countryCodeField.value = userLocation.countryCode;

        // Update the region banner with a greeting based on detected city and country.
        setRegionBasedOnLocation(userLocation);
    }

    /**
     * Sets the pricing for users detected to be in Israel.
     * Updates the pricing container with special pricing tiers and disables location change.
     */
    function setPricingForIsrael() {
        const priceContainer = document.getElementById('pricing');
        if (priceContainer) {
            priceContainer.innerHTML = '';

            // Special pricing tiers for Israel.
            const pricingTiers = {
                Creator: { weekly: 35, monthly: 99 },
                Pro: { weekly: 65, monthly: 199 },
                Enterprise: { weekly: null, monthly: 699 },
                MediaPack: { weekly: null, monthly: 2500 }
            };

            // Create and append a paragraph element for each pricing tier.
            Object.entries(pricingTiers).forEach(([tier, prices]) => {
                const tierElement = document.createElement('p');
                tierElement.textContent = `${tier} - Weekly: ${prices.weekly ? `$${prices.weekly}` : 'N/A'}, Monthly: $${prices.monthly}`;
                priceContainer.appendChild(tierElement);
            });
        }
        disableLocationChange();
    }

    /**
     * Sets the default pricing for users not in Israel.
     * Updates the pricing container with general pricing tiers.
     */
    function setDefaultPricing() {
        const priceContainer = document.getElementById('pricing');
        if (priceContainer) {
            priceContainer.innerHTML = '';

            // Default pricing tiers.
            const pricingTiers = {
                Creator: { weekly: 15, monthly: 59 },
                Pro: { weekly: 35, monthly: 99 },
                Enterprise: { weekly: null, monthly: 499 },
                MediaPack: { weekly: null, monthly: 2000 }
            };

            Object.entries(pricingTiers).forEach(([tier, prices]) => {
                const tierElement = document.createElement('p');
                tierElement.textContent = `${tier} - Weekly: ${prices.weekly ? `$${prices.weekly}` : 'N/A'}, Monthly: $${prices.monthly}`;
                priceContainer.appendChild(tierElement);
            });
        }
    }

    /**
     * Disables the location change control to prevent users in a special region from modifying their location.
     */
    function disableLocationChange() {
        const locationSelect = document.getElementById('location-select');
        if (locationSelect) {
            locationSelect.disabled = true;
            const warningMessage = document.createElement('p');
            warningMessage.textContent = 'Your location is locked to Israel and cannot be changed.';
            warningMessage.classList.add('warning-message');
            locationSelect.parentElement.appendChild(warningMessage);
        }
    }

    /**
     * Sets a region-based banner message based on the user's detected location.
     *
     * @param {Object} userLocation - The object containing user location details.
     */
    function setRegionBasedOnLocation(userLocation) {
        const regionBanner = document.getElementById('region-banner');
        if (regionBanner) {
            // Update banner with a friendly greeting using city and country.
            regionBanner.textContent = `Welcome from ${userLocation.city}, ${userLocation.country}!`;
        }

        // Send location data to the backend for further processing if needed.
        sendLocationToBackend(userLocation);
    }

    /**
     * Sends the detected user location data to the backend.
     *
     * @param {Object} locationData - The location data object.
     */
    function sendLocationToBackend(locationData) {
        fetch('/update-location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
                // Include CSRF tokens here if required by your backend.
            },
            body: JSON.stringify(locationData)
        })
            .then(response => response.json())
            .then(data => {
                console.log('Location updated on backend:', data);
            })
            .catch(error => {
                console.error('Error sending location data to backend:', error);
            });
    }
});
