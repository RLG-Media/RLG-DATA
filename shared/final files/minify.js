// Minified version of critical JS functionality for RLG Data and RLG Fans
(function () {
    // Global variable to hold state or configuration
    const config = {
        apiEndpoint: 'https://api.rlgdata.com', // Update with the actual API endpoint
        debugMode: false, // Set to true for detailed logs
    };

    // Helper function to log debug messages
    function logDebug(message) {
        if (config.debugMode) {
            console.debug(`[DEBUG]: ${message}`);
        }
    }

    // Function to handle API requests
    function fetchData(url, method = 'GET', body = null) {
        logDebug(`Requesting: ${url} with method: ${method}`);
        return fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            logDebug(`Error during fetch: ${error.message}`);
            throw error;
        });
    }

    // Function to initialize the dashboard
    function initDashboard() {
        logDebug('Initializing Dashboard...');
        fetchData(`${config.apiEndpoint}/dashboard/data`)
            .then(data => {
                displayDashboardData(data);
            })
            .catch(error => {
                console.error(`Dashboard initialization failed: ${error.message}`);
            });
    }

    // Function to display dashboard data
    function displayDashboardData(data) {
        const dashboardElement = document.getElementById('dashboard');
        if (dashboardElement) {
            dashboardElement.innerHTML = `
                <h2>Data Overview</h2>
                <p>Users: ${data.users}</p>
                <p>Engagement: ${data.engagement}</p>
                <p>Content Views: ${data.contentViews}</p>
            `;
        } else {
            console.warn('Dashboard element not found!');
        }
    }

    // Lazy load images for better performance
    function lazyLoadImages() {
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => {
            img.setAttribute('src', img.getAttribute('data-src'));
            img.onload = () => {
                img.removeAttribute('data-src');
                logDebug(`Image loaded: ${img.src}`);
            };
        });
    }

    // Toggle navigation menu visibility on mobile
    function toggleMenu() {
        const menu = document.getElementById('mobile-menu');
        if (menu) {
            menu.classList.toggle('active');
            logDebug('Menu toggled');
        }
    }

    // Form validation function
    function validateForm(form) {
        const name = form.querySelector('[name="name"]');
        const email = form.querySelector('[name="email"]');
        const message = form.querySelector('[name="message"]');
        if (!name.value || !email.value || !message.value) {
            alert('Please fill out all fields.');
            return false;
        }
        return true;
    }

    // Submit form function
    function submitForm(form) {
        if (validateForm(form)) {
            const formData = new FormData(form);
            fetchData(`${config.apiEndpoint}/contact/submit`, 'POST', formData)
                .then(response => {
                    alert('Your message has been sent!');
                })
                .catch(error => {
                    alert('There was an error submitting your message. Please try again.');
                });
        }
    }

    // Event listener to initialize functions on DOM load
    document.addEventListener('DOMContentLoaded', function () {
        logDebug('Document loaded');

        // Initialize dashboard data
        initDashboard();

        // Lazy load images
        lazyLoadImages();

        // Bind mobile menu toggle event
        const mobileMenuButton = document.getElementById('menu-toggle-button');
        if (mobileMenuButton) {
            mobileMenuButton.addEventListener('click', toggleMenu);
        }

        // Bind contact form submission
        const contactForm = document.getElementById('contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', function (e) {
                e.preventDefault();
                submitForm(contactForm);
            });
        }
    });
})();

const zlib = require('zlib');
const compressedContent = zlib.gzipSync(result.code);
fs.writeFileSync(outputFilePath + '.gz', compressedContent);
