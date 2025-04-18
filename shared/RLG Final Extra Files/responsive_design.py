from flask import Flask, render_template
from flask_templating import render_with_layout
import logging

# Initialize Flask app
app = Flask(__name__)

# Set up logging to track responsive design issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    """
    This route renders the homepage with the responsive design elements.
    """
    try:
        # Adjust the layout depending on the device type (desktop, mobile, etc.)
        layout = get_device_layout()
        return render_template("index.html", layout=layout)
    except Exception as e:
        logger.error(f"Error loading home page: {str(e)}")
        return render_template("error.html", message="Error loading page. Please try again later.")


def get_device_layout():
    """
    Determines the appropriate layout for the user's device.
    Returns:
        str: The layout type ('desktop', 'mobile', 'tablet').
    """
    # Check if the request is mobile or desktop based on the user-agent
    user_agent = request.headers.get('User-Agent').lower()
    
    if 'mobile' in user_agent:
        layout = 'mobile'
    elif 'tablet' in user_agent:
        layout = 'tablet'
    else:
        layout = 'desktop'
    
    logger.info(f"Detected device layout: {layout}")
    return layout


@app.route('/settings')
def settings():
    """
    A settings page that also supports responsive design.
    """
    try:
        layout = get_device_layout()
        return render_template("settings.html", layout=layout)
    except Exception as e:
        logger.error(f"Error loading settings page: {str(e)}")
        return render_template("error.html", message="Error loading settings page.")


@app.route('/about')
def about():
    """
    A simple About page with responsive design.
    """
    try:
        layout = get_device_layout()
        return render_template("about.html", layout=layout)
    except Exception as e:
        logger.error(f"Error loading about page: {str(e)}")
        return render_template("error.html", message="Error loading about page.")


@app.before_first_request
def setup_responsive_design():
    """
    This function will run before the first request to ensure responsive design settings are applied.
    This could be useful for any global adjustments to mobile/tablet/desktop views.
    """
    logger.info("Responsive design setup complete.")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
