import os
from flask import Flask, jsonify, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

# Set up logging to track any issues with PWA
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__)

# PWA Cache and Manifest Configuration
PWA_CACHE_FILES = [
    '/static/js/main.js',
    '/static/css/main.css',
    '/static/images/logo.png',
    '/offline',  # Custom offline page
    # Add other files required for offline support
]

PWA_MANIFEST = {
    "name": "RLG Data & Fans",
    "short_name": "RLG",
    "description": "Empowering creators and businesses with real-time analytics and tools",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#000000",
    "icons": [
        {
            "src": "/static/images/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/static/images/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

# Enable ProxyFix for correct handling of proxies, if behind a reverse proxy (like nginx)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/')
def home():
    """
    Home route for the application.
    Returns the main view to the user.
    """
    return render_template('index.html')


@app.route('/offline')
def offline():
    """
    Provides a fallback offline page if the user is offline.
    """
    return render_template('offline.html')


@app.route('/pwa-manifest')
def manifest():
    """
    Returns the manifest for PWA support, enabling app-like behavior.
    """
    return jsonify(PWA_MANIFEST)


@app.route('/service-worker.js')
def service_worker():
    """
    Service Worker file that handles caching and offline support for the app.
    This file intercepts network requests and serves them from cache if offline.
    """
    service_worker_code = """
    const CACHE_NAME = 'rlg-cache-v1';
    const PWA_CACHE_FILES = """ + str(PWA_CACHE_FILES) + """;
    
    self.addEventListener('install', (event) => {
        event.waitUntil(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.addAll(PWA_CACHE_FILES);
            })
        );
    });

    self.addEventListener('fetch', (event) => {
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(event.request);
            })
        );
    });

    self.addEventListener('activate', (event) => {
        const cacheWhitelist = [CACHE_NAME];
        event.waitUntil(
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheWhitelist.indexOf(cacheName) === -1) {
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
        );
    });
    """
    return Response(service_worker_code, mimetype="application/javascript")


@app.route('/pwa-update')
def pwa_update():
    """
    Endpoint to check for updates in PWA files.
    This can be extended to periodically check for new versions.
    """
    # In a real-world scenario, you can implement version checking here.
    return jsonify({"status": "success", "message": "PWA files are up-to-date"})


@app.before_first_request
def setup_pwa_support():
    """
    Initializes PWA support by ensuring required static files and resources are ready.
    """
    try:
        # Ensure necessary files are present
        for file in PWA_CACHE_FILES:
            if not os.path.exists(file):
                logger.warning(f"PWA Cache File Missing: {file}")

        logger.info("PWA support setup complete.")
    except Exception as e:
        logger.error(f"Error setting up PWA support: {str(e)}")


if __name__ == '__main__':
    # Enable the app to run in production mode if environment variable is set
    app.run(debug=os.environ.get('FLASK_ENV') == 'development', host='0.0.0.0', port=5000)
