// home_page.js
// Handles interactivity and dynamic content for the home page of RLG Data and RLG Fans

// Event listener for DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
    initializeHeroAnimation();
    setupTestimonialsCarousel();
    setupCTAButtonHandlers();
    enableDarkModeToggle();
    optimizePerformance();
});

/**
 * Initializes the hero section animation for engaging visuals.
 */
function initializeHeroAnimation() {
    const heroText = document.querySelector(".hero h1");
    if (heroText) {
        heroText.classList.add("animate-fade-in");
    }
}

/**
 * Sets up a testimonials carousel for dynamic user feedback.
 */
function setupTestimonialsCarousel() {
    const testimonials = document.querySelectorAll(".testimonial-item");
    if (testimonials.length > 1) {
        let currentIndex = 0;
        setInterval(() => {
            testimonials.forEach((item, index) => {
                item.style.display = index === currentIndex ? "block" : "none";
            });
            currentIndex = (currentIndex + 1) % testimonials.length;
        }, 5000); // Rotate every 5 seconds
    }
}

/**
 * Attaches event handlers to call-to-action (CTA) buttons.
 */
function setupCTAButtonHandlers() {
    const ctaButtons = document.querySelectorAll("button[onclick]");
    ctaButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            const target = button.getAttribute("onclick").split("'")[1];
            if (target) {
                window.location.href = target;
            }
        });
    });
}

/**
 * Enables a dark mode toggle feature for better user experience.
 */
function enableDarkModeToggle() {
    const darkModeToggle = document.querySelector("#dark-mode-toggle");
    if (darkModeToggle) {
        darkModeToggle.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            const isDarkMode = document.body.classList.contains("dark-mode");
            localStorage.setItem("darkMode", isDarkMode);
        });

        // Set the initial dark mode state based on user preference
        if (localStorage.getItem("darkMode") === "true") {
            document.body.classList.add("dark-mode");
        }
    }
}

/**
 * Optimizes the page performance by deferring non-critical tasks.
 */
function optimizePerformance() {
    // Lazy load images
    const images = document.querySelectorAll("img");
    images.forEach((img) => {
        img.setAttribute("loading", "lazy");
    });

    // Optimize heavy computations for idle time
    if ("requestIdleCallback" in window) {
        requestIdleCallback(() => {
            prefetchContent();
        });
    } else {
        setTimeout(() => {
            prefetchContent();
        }, 2000);
    }
}

/**
 * Prefetches content to improve perceived load time.
 */
function prefetchContent() {
    const links = [
        "/features.html",
        "/pricing.html",
        "/about.html",
        "/contact.html",
    ];
    links.forEach((link) => {
        const linkElement = document.createElement("link");
        linkElement.rel = "prefetch";
        linkElement.href = link;
        document.head.appendChild(linkElement);
    });
}

/**
 * Logs analytics events for user interactions.
 * @param {string} event - The name of the event
 * @param {object} data - Additional data to log
 */
function logAnalyticsEvent(event, data = {}) {
    console.log(`Analytics Event: ${event}`, data);

    // Example of sending the event to a backend analytics service
    fetch("/api/log-event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event, ...data }),
    }).catch((error) => console.error("Analytics error:", error));
}

// Log page view analytics
logAnalyticsEvent("page_view", { page: "home", timestamp: new Date().toISOString() });

/**
 * Monitors and displays network status.
 */
function monitorNetworkStatus() {
    const statusElement = document.querySelector("#network-status");
    if (statusElement) {
        const updateStatus = () => {
            if (navigator.onLine) {
                statusElement.textContent = "Online";
                statusElement.classList.add("online");
                statusElement.classList.remove("offline");
            } else {
                statusElement.textContent = "Offline";
                statusElement.classList.add("offline");
                statusElement.classList.remove("online");
            }
        };
        window.addEventListener("online", updateStatus);
        window.addEventListener("offline", updateStatus);
        updateStatus(); // Initialize status
    }
}

// Initialize network monitoring
monitorNetworkStatus();
