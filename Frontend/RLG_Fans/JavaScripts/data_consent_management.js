document.addEventListener("DOMContentLoaded", function () {
    const consentModal = document.getElementById("consent-modal");
    const acceptAllButton = document.getElementById("accept-all");
    const rejectAllButton = document.getElementById("reject-all");
    const customizeButton = document.getElementById("customize-consent");
    const savePreferencesButton = document.getElementById("save-preferences");
    const consentForm = document.getElementById("consent-form");
    const consentCategories = document.querySelectorAll(".consent-category");

    const consentStorageKey = "user_consent_preferences";

    // Show consent modal if no preference exists
    function checkConsentStatus() {
        const storedConsent = localStorage.getItem(consentStorageKey);
        if (!storedConsent) {
            consentModal.style.display = "block";
        }
    }

    // Save consent preferences
    function saveConsentPreferences(preferences) {
        localStorage.setItem(consentStorageKey, JSON.stringify(preferences));
        consentModal.style.display = "none";
        sendConsentToServer(preferences);
    }

    // Send consent data to server
    async function sendConsentToServer(preferences) {
        try {
            await fetch("/api/consent-management", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(preferences),
            });
        } catch (error) {
            console.error("Error sending consent data:", error);
        }
    }

    // Accept all tracking
    acceptAllButton.addEventListener("click", function () {
        const allConsent = {
            analytics: true,
            advertising: true,
            functional: true,
            socialMedia: true
        };
        saveConsentPreferences(allConsent);
    });

    // Reject all tracking
    rejectAllButton.addEventListener("click", function () {
        const noConsent = {
            analytics: false,
            advertising: false,
            functional: false,
            socialMedia: false
        };
        saveConsentPreferences(noConsent);
    });

    // Open customization panel
    customizeButton.addEventListener("click", function () {
        consentForm.style.display = "block";
    });

    // Save customized preferences
    savePreferencesButton.addEventListener("click", function () {
        const preferences = {};
        consentCategories.forEach(category => {
            preferences[category.name] = category.checked;
        });
        saveConsentPreferences(preferences);
    });

    // Check consent status on load
    checkConsentStatus();
});
