/**
 * RLG_Data_register.js
 *
 * This script handles the registration and sign-up process for RLG Data & RLG Fans.
 * It captures user input, detects the user's geolocation, applies region-based pricing
 * (with hard-locked "Special Region" pricing for Israel), and sends the registration
 * details to the backend. For users in Israel, the response includes the message:
 * "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד."
 *
 * Note: In production, passwords must be hashed on the server, and sensitive data should
 * be handled securely.
 */

document.addEventListener("DOMContentLoaded", function() {
    const registrationForm = document.getElementById("registration-form");
    
    if (registrationForm) {
        registrationForm.addEventListener("submit", function(event) {
            event.preventDefault();
            registerUser();
        });
    }
    
    /**
     * Captures the form data, fetches geolocation, and sends registration data to the backend.
     */
    function registerUser() {
        // Retrieve form values
        const username = document.getElementById("username").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        
        if (!username || !email || !password) {
            alert("Please fill in all required fields.");
            return;
        }
        
        // Use ipapi.co to fetch geolocation data
        fetch("https://ipapi.co/json/")
            .then(response => response.json())
            .then(geoData => {
                if (geoData.error) {
                    throw new Error(geoData.reason || "Geolocation error");
                }
                
                // Build a user location object
                const userLocation = {
                    country: geoData.country_name,    // e.g., "Israel"
                    countryCode: geoData.country_code,  // e.g., "IL"
                    region: geoData.region,             // e.g., "Tel Aviv District"
                    city: geoData.city,                 // e.g., "Tel Aviv"
                    ip: geoData.ip                      // Detected IP address
                };
                
                console.log("User location detected:", userLocation);
                
                // Determine if the user's location should be locked (for Special Region pricing)
                let locationLocked = false;
                let specialMessage = "";
                if (userLocation.countryCode === "IL") {
                    locationLocked = true;
                    specialMessage = "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד.";
                }
                
                // Build the registration payload
                const payload = {
                    username: username,
                    email: email,
                    password: password,  // NOTE: In production, the server should hash this value.
                    location: userLocation,
                    locationLocked: locationLocked
                };
                
                // Send registration data to the backend
                fetch("/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                        // Include CSRF token here if needed.
                    },
                    body: JSON.stringify(payload)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Registration failed with status " + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Registration response:", data);
                    if (data.error) {
                        alert("Registration failed: " + data.error);
                    } else {
                        let msg = "Registration successful!";
                        if (data.user && data.user.special_message) {
                            msg += "\n" + data.user.special_message;
                        }
                        alert(msg);
                        // Redirect to the pricing/dashboard page after successful registration.
                        window.location.href = "/dashboard";
                    }
                })
                .catch(error => {
                    console.error("Error during registration:", error);
                    alert("An error occurred during registration. Please try again.");
                });
            })
            .catch(error => {
                console.error("Error fetching geolocation:", error);
                alert("Unable to determine your location. Please try again.");
            });
    }
});
