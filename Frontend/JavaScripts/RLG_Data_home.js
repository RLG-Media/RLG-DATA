document.addEventListener("DOMContentLoaded", function () {
    // On page load, fetch home data from the backend
    fetchHomeData();

    /**
     * Fetches home data from the backend.
     * Expected response should include:
     *   - user: (object or null)
     *   - pricing: (object with pricing tiers)
     *   - region_name: string (detected region or "Special Region" for Israel)
     *   - special_message: string (if applicable)
     */
    function fetchHomeData() {
        // Replace '/api/home' with your actual endpoint that returns home page data.
        fetch("/api/home")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok. Status: " + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log("Home data received:", data);
                updateHomePage(data);
            })
            .catch(error => {
                console.error("Error fetching home data:", error);
                // Optionally, show a friendly error message in the UI
                const container = document.getElementById("home-container");
                if (container) {
                    container.innerHTML = "<p>We're sorry, but we were unable to load your data. Please try again later.</p>";
                }
            });
    }

    /**
     * Updates the home page UI based on the received data.
     * If the user is registered, displays personalized pricing and region details.
     * For unregistered users, displays a prompt to register and a preview of pricing.
     *
     * @param {Object} data - The data returned from the backend.
     */
    function updateHomePage(data) {
        // Assume your HTML contains elements with these IDs:
        // "welcome-message", "region-banner", "pricing-container", "register-prompt"
        const welcomeMessageEl = document.getElementById("welcome-message");
        const regionBannerEl = document.getElementById("region-banner");
        const pricingContainerEl = document.getElementById("pricing-container");
        const registerPromptEl = document.getElementById("register-prompt");

        if (data.user) {
            // Registered user: display personalized details
            welcomeMessageEl.textContent = `Hello, ${data.user.username}!`;
            regionBannerEl.textContent = `Your location: ${data.region_name}`;
            
            // Build pricing details list from pricing tiers
            let pricingHTML = "<h3>Your Pricing Plan</h3><ul>";
            for (let [tier, prices] of Object.entries(data.pricing)) {
                pricingHTML += `<li>${tier} - Weekly: ${prices.weekly ? "$" + prices.weekly : "N/A"}, Monthly: ${prices.monthly ? "$" + prices.monthly : "N/A"}</li>`;
            }
            pricingHTML += "</ul>";
            pricingContainerEl.innerHTML = pricingHTML;

            // If special message exists (e.g., for Special Region users), display it.
            if (data.special_message) {
                const specialMsgEl = document.createElement("p");
                specialMsgEl.className = "special-message";
                specialMsgEl.textContent = data.special_message;
                pricingContainerEl.appendChild(specialMsgEl);
            }
            // Hide registration prompt for registered users.
            if (registerPromptEl) registerPromptEl.style.display = "none";
        } else {
            // Unregistered user: show a generic welcome and prompt to register.
            welcomeMessageEl.textContent = "Welcome to RLG Data & RLG Fans!";
            regionBannerEl.textContent = `Detected Region: ${data.region_name || "Unknown"}`;
            
            // For unregistered users, do not show full pricing details.
            pricingContainerEl.innerHTML = "<p>To view personalized pricing and features, please register.</p>";
            
            // Show a prominent prompt/link to register.
            if (registerPromptEl) {
                registerPromptEl.innerHTML = `<a href="/register" class="btn btn-primary">Register Now</a>`;
                registerPromptEl.style.display = "block";
            }
        }
    }
});
