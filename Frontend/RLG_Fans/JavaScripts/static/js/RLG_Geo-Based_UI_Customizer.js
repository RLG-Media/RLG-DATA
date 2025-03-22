// RLG_Geo-Based_UI_Customizer.js
// ✅ AI-Powered Geo-Based UI Customization for RLG Data & RLG Fans

document.addEventListener("DOMContentLoaded", () => {
    getUserLocation();
});

// 🌍 Fetch User's Location via IP & Geolocation API
async function getUserLocation() {
    try {
        let geoData = await fetchUserIP();
        applyGeoCustomizations(geoData);
    } catch (error) {
        console.error("Geo-Location Error:", error);
    }
}

// 🛰️ Fetch User IP & Geo Data
async function fetchUserIP() {
    try {
        const response = await fetch("https://ipapi.co/json/");
        const data = await response.json();
        return {
            country: data.country_name,
            countryCode: data.country_code,
            city: data.city,
            region: data.region,
            currency: data.currency,
            timezone: data.timezone,
            latitude: data.latitude,
            longitude: data.longitude
        };
    } catch (error) {
        console.error("IP Fetch Error:", error);
        return {};
    }
}

// 🎨 Apply Region-Based UI Customization
function applyGeoCustomizations({ country, countryCode, city, region, currency, timezone }) {
    if (!country) return;

    // Store geo data locally for optimized re-use
    localStorage.setItem("RLG_User_Location", JSON.stringify({ country, countryCode, city, region, currency, timezone }));

    // 🏷️ Set Page Language
    updateLanguage(countryCode);

    // 💲 Adjust Regional Pricing
    adjustPricing(country);

    // 🎨 Modify UI Based on Region
    customizeUIForRegion(country, region, city);

    console.log(`✅ UI Customized for ${city}, ${region}, ${country} (${currency}, ${timezone})`);
}

// 🌐 Auto-Language Switching
function updateLanguage(countryCode) {
    const langMapping = {
        "FR": "fr", "ES": "es", "DE": "de", "IT": "it", "CN": "zh", "JP": "ja", "IN": "hi",
        "BR": "pt", "RU": "ru", "SA": "ar", "IL": "he", "ZA": "af", "NG": "yo"
    };
    const selectedLang = langMapping[countryCode] || "en";
    document.documentElement.setAttribute("lang", selectedLang);
    console.log(`🌍 Language set to: ${selectedLang.toUpperCase()}`);
}

// 💲 Region-Based Pricing Adjustment
function adjustPricing(country) {
    const pricingTable = {
        "United States": "$59/month", "Canada": "C$75/month", "United Kingdom": "£49/month",
        "Germany": "€55/month", "France": "€55/month", "Israel": "$99/month", "South Africa": "R899/month",
        "Nigeria": "₦30,000/month", "India": "₹4,999/month"
    };

    let finalPrice = pricingTable[country] || "$59/month"; // Default global price
    document.querySelectorAll(".rlg-price").forEach(el => (el.textContent = finalPrice));
    console.log(`💰 Pricing Adjusted: ${finalPrice}`);
}

// 🎨 Region-Specific UI Customization
function customizeUIForRegion(country, region, city) {
    const regionThemes = {
        "Middle East": { bg: "#FFD700", text: "#333" },
        "Europe": { bg: "#0057B8", text: "#FFF" },
        "Africa": { bg: "#1B5E20", text: "#FFD700" },
        "Asia": { bg: "#FF5722", text: "#FFF" },
        "Latin America": { bg: "#F57C00", text: "#FFF" }
    };

    let selectedTheme = regionThemes["Europe"];
    if (country === "South Africa" || country === "Nigeria" || country === "Kenya") selectedTheme = regionThemes["Africa"];
    if (country === "United Arab Emirates" || country === "Saudi Arabia") selectedTheme = regionThemes["Middle East"];
    if (country === "Japan" || country === "China" || country === "India") selectedTheme = regionThemes["Asia"];
    if (country === "Brazil" || country === "Argentina") selectedTheme = regionThemes["Latin America"];

    document.body.style.backgroundColor = selectedTheme.bg;
    document.body.style.color = selectedTheme.text;
    console.log(`🎨 UI Theme Applied for ${country} - ${region}`);
}

// 📍 Smart Caching & Auto-Refresh for Returning Users
function loadPreviousLocation() {
    let storedData = localStorage.getItem("RLG_User_Location");
    if (storedData) {
        applyGeoCustomizations(JSON.parse(storedData));
        console.log("♻️ Previous Location Restored");
    }
}

// 🏁 Initialize
loadPreviousLocation();
