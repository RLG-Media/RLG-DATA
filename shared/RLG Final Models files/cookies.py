from flask import request, jsonify, make_response
import datetime

class CookiesManager:
    """
    A class to handle cookies for user tracking, advertising, upselling,
    and improving the overall user experience on the RLG platform.
    """

    def __init__(self):
        self.cookie_settings = {
            "secure": True,  # Ensure cookies are sent only over HTTPS
            "httponly": True,  # Prevent cookies from being accessed via JavaScript
            "samesite": "Lax",  # Protect against cross-site request forgery
        }

    def set_cookie(self, response, key, value, expires_days=30):
        """
        Set a cookie with the given key and value.

        :param response: Flask response object
        :param key: Cookie name
        :param value: Cookie value
        :param expires_days: Duration for the cookie to expire
        """
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=expires_days)
        response.set_cookie(
            key,
            value,
            expires=expires,
            **self.cookie_settings
        )

    def get_cookie(self, key):
        """
        Retrieve the value of a specific cookie.

        :param key: Cookie name
        :return: Cookie value or None if the cookie doesn't exist
        """
        return request.cookies.get(key)

    def delete_cookie(self, response, key):
        """
        Delete a specific cookie.

        :param response: Flask response object
        :param key: Cookie name
        """
        response.set_cookie(key, "", expires=0, **self.cookie_settings)

    def track_user_behavior(self):
        """
        Track user behavior for analytics and personalized recommendations.

        :return: JSON object with tracking confirmation
        """
        user_ip = request.remote_addr
        user_agent = request.headers.get("User-Agent")
        visited_pages = self.get_cookie("visited_pages")
        updated_pages = visited_pages + f",{request.path}" if visited_pages else request.path

        # Update the visited_pages cookie
        response = make_response(jsonify({"status": "Tracking updated"}))
        self.set_cookie(response, "visited_pages", updated_pages, expires_days=30)

        # Example logging or saving data to a database (replace with actual implementation)
        print(f"User IP: {user_ip}, User Agent: {user_agent}, Pages: {updated_pages}")
        return response

    def upsell_features(self):
        """
        Display personalized upselling opportunities based on user behavior.

        :return: JSON object with recommended features
        """
        visited_pages = self.get_cookie("visited_pages")
        recommendations = []

        if visited_pages:
            if "analytics" in visited_pages:
                recommendations.append("Upgrade to Pro Analytics!")
            if "dashboard" in visited_pages:
                recommendations.append("Enable Advanced Dashboard Features!")

        return jsonify({"recommendations": recommendations})

    def consent_banner(self):
        """
        Show a consent banner to the user for cookie management.

        :return: HTML content for the consent banner
        """
        return """
        <div id="cookie-consent-banner">
            <p>We use cookies to improve your experience and provide personalized recommendations.
            By continuing to use our platform, you consent to our cookie policy.</p>
            <button onclick="acceptCookies()">Accept</button>
            <button onclick="declineCookies()">Decline</button>
        </div>
        <script>
            function acceptCookies() {
                fetch('/cookies/accept', { method: 'POST' });
                document.getElementById('cookie-consent-banner').style.display = 'none';
            }
            function declineCookies() {
                fetch('/cookies/decline', { method: 'POST' });
                document.getElementById('cookie-consent-banner').style.display = 'none';
            }
        </script>
        """

# Flask routes to integrate cookie functionalities
from flask import Flask, request, jsonify

app = Flask(__name__)
cookies_manager = CookiesManager()

@app.route("/cookies/accept", methods=["POST"])
def accept_cookies():
    response = make_response(jsonify({"status": "Cookies accepted"}))
    cookies_manager.set_cookie(response, "cookies_accepted", "true", expires_days=365)
    return response

@app.route("/cookies/decline", methods=["POST"])
def decline_cookies():
    response = make_response(jsonify({"status": "Cookies declined"}))
    cookies_manager.delete_cookie(response, "cookies_accepted")
    return response

@app.route("/track", methods=["GET"])
def track_user():
    return cookies_manager.track_user_behavior()

@app.route("/upsell", methods=["GET"])
def upsell():
    return cookies_manager.upsell_features()

if __name__ == "__main__":
    app.run(debug=True)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict'
)
