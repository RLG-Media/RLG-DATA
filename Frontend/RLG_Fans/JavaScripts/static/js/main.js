// Main JavaScript File

// Document Ready Function
document.addEventListener("DOMContentLoaded", () => {
    initNavbarToggle();
    initModalControls();
    initFormValidation();
    initThemeToggle();
    initDynamicContentLoaders();
    setupEventListeners();
    initChatWidget();
    console.log("Main.js loaded successfully!");
});

// Navbar Toggle
function initNavbarToggle() {
    const navbarToggle = document.querySelector(".navbar-toggle");
    const navbarMenu = document.querySelector(".navbar-menu");

    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener("click", () => {
            navbarMenu.classList.toggle("open");
        });
    }
}

// Modal Controls
function initModalControls() {
    const modalTriggers = document.querySelectorAll("[data-modal-target]");
    const modals = document.querySelectorAll(".modal");

    modalTriggers.forEach(trigger => {
        trigger.addEventListener("click", () => {
            const target = trigger.getAttribute("data-modal-target");
            const modal = document.querySelector(target);
            if (modal) modal.classList.add("active");
        });
    });

    modals.forEach(modal => {
        const closeModal = modal.querySelector(".modal-close");
        if (closeModal) {
            closeModal.addEventListener("click", () => {
                modal.classList.remove("active");
            });
        }

        modal.addEventListener("click", (event) => {
            if (event.target === modal) modal.classList.remove("active");
        });
    });
}

// Form Validation
function initFormValidation() {
    const forms = document.querySelectorAll(".needs-validation");

    forms.forEach(form => {
        form.addEventListener("submit", (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add("was-validated");
        });
    });
}

// Theme Toggle
function initThemeToggle() {
    const themeToggle = document.querySelector("#theme-toggle");
    const body = document.body;

    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            body.classList.toggle("dark-mode");
            const isDarkMode = body.classList.contains("dark-mode");
            localStorage.setItem("theme", isDarkMode ? "dark" : "light");
        });

        // Apply saved theme preference on load
        const savedTheme = localStorage.getItem("theme");
        if (savedTheme === "dark") {
            body.classList.add("dark-mode");
        }
    }
}

// Dynamic Content Loaders
function initDynamicContentLoaders() {
    const dynamicElements = document.querySelectorAll("[data-load-content]");

    dynamicElements.forEach(element => {
        const url = element.getAttribute("data-load-content");

        if (url) {
            fetch(url)
                .then(response => response.text())
                .then(content => {
                    element.innerHTML = content;
                })
                .catch(error => {
                    console.error("Error loading dynamic content:", error);
                });
        }
    });
}

// Utility Functions
function showNotification(message, type = "success") {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Event Listeners for Buttons and Links
function setupEventListeners() {
    const actionButtons = document.querySelectorAll("[data-action]");
    const links = document.querySelectorAll("[data-link]");

    actionButtons.forEach(button => {
        button.addEventListener("click", (event) => {
            const action = button.getAttribute("data-action");
            handleAction(action, event);
        });
    });

    links.forEach(link => {
        link.addEventListener("click", (event) => {
            const url = link.getAttribute("data-link");
            if (url) {
                event.preventDefault();
                navigateTo(url);
            }
        });
    });
}

// Action Handlers
function handleAction(action, event) {
    switch (action) {
        case "save":
            console.log("Save action triggered.");
            showNotification("Data saved successfully!", "success");
            break;
        case "delete":
            console.log("Delete action triggered.");
            showNotification("Item deleted successfully.", "error");
            break;
        default:
            console.log("Unknown action:", action);
    }
}

// Navigation
function navigateTo(url) {
    console.log("Navigating to:", url);
    const contentContainer = document.querySelector("#content-container");
    if (contentContainer) {
        fetch(url)
            .then(response => response.text())
            .then(html => {
                contentContainer.innerHTML = html;
            })
            .catch(error => {
                console.error("Navigation error:", error);
                showNotification("Failed to load page.", "error");
            });
    } else {
        window.location.href = url;
    }
}

// Chat Widget
function initChatWidget() {
    const chatIcon = document.querySelector("#chat-icon");
    const chatPopup = document.querySelector("#chat-popup");

    if (chatIcon && chatPopup) {
        chatIcon.addEventListener("click", () => {
            const isOpen = chatPopup.style.display === "block";
            chatPopup.style.display = isOpen ? "none" : "block";
        });

        document.addEventListener("click", (event) => {
            if (!chatPopup.contains(event.target) && event.target !== chatIcon) {
                chatPopup.style.display = "none";
            }
        });
    }
}
