document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    
    if (loginForm) {
        loginForm.addEventListener("submit", function (event) {
            event.preventDefault();
            userLogin();
        });
    }

    /**
     * Handles user login by capturing form data and sending it to the backend.
     * On success, it stores the authentication token and redirects the user.
     * If the user is from Israel (special region), the response will include the message:
     * "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד."
     */
    function userLogin() {
        // Retrieve form values
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;

        // Validate inputs
        if (!username || !password) {
            alert("Please enter both username and password.");
            return;
        }

        // Build the payload for login
        const payload = {
            username: username,
            password: password
        };

        // Send the login request to the backend endpoint "/login"
        fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
                // Add CSRF token header if your backend requires it
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Login failed with status " + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Login successful:", data);
            // Store the authentication token in localStorage for later use
            if (data.token) {
                localStorage.setItem("authToken", data.token);
            }
            // Construct a welcome message. If location is locked (e.g., Israeli user), include the special message.
            let message = "Login successful. Welcome, " + data.user.username + "!";
            if (data.user.location_locked && data.user.special_message) {
                message += "\n" + data.user.special_message;
            }
            alert(message);
            // Redirect the user to the dashboard or pricing page after successful login.
            window.location.href = "/dashboard";
        })
        .catch(error => {
            console.error("Error during login:", error);
            alert("Login failed: " + error.message);
        });
    }
});
