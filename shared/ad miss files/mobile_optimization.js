/**
 * mobile_optimization.js
 * Script for optimizing mobile experience for RLG Data and RLG Fans.
 * Ensures responsiveness, performance, and accessibility.
 */

// Utility function to detect mobile devices
const isMobileDevice = () => {
  return /Android|iPhone|iPad|iPod|Opera Mini|IEMobile|WPDesktop/i.test(navigator.userAgent);
};

// Function to adjust layout for mobile
const optimizeLayoutForMobile = () => {
  if (isMobileDevice()) {
    document.body.classList.add("mobile-optimized");

    // Adjust header
    const header = document.querySelector(".header");
    if (header) {
      header.style.fontSize = "1.2rem";
      header.style.padding = "10px 15px";
    }

    // Optimize navigation menu
    const navMenu = document.querySelector(".navigation-menu");
    if (navMenu) {
      navMenu.classList.add("mobile-nav");
      const navToggle = document.createElement("button");
      navToggle.textContent = "☰ Menu";
      navToggle.classList.add("nav-toggle");
      navToggle.addEventListener("click", () => {
        navMenu.classList.toggle("open");
      });
      navMenu.parentElement.insertBefore(navToggle, navMenu);
    }

    // Adjust font sizes and button padding
    document.querySelectorAll("h1, h2, h3, p, button").forEach((element) => {
      element.style.fontSize = "clamp(14px, 4vw, 18px)";
      if (element.tagName === "BUTTON") {
        element.style.padding = "10px 15px";
      }
    });

    // Optimize table views for smaller screens
    document.querySelectorAll("table").forEach((table) => {
      table.style.display = "block";
      table.style.overflowX = "auto";
      table.style.width = "100%";
    });
  }
};

// Function to lazy-load images for performance
const enableLazyLoading = () => {
  const images = document.querySelectorAll("img[data-src]");
  const observer = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute("data-src");
          observer.unobserve(img);
        }
      });
    },
    {
      rootMargin: "50px",
      threshold: 0.1,
    }
  );

  images.forEach((img) => observer.observe(img));
};

// Function to enhance touch responsiveness
const enhanceTouchExperience = () => {
  if (isMobileDevice()) {
    document.body.style.touchAction = "manipulation";

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", (event) => {
        event.preventDefault();
        const target = document.querySelector(anchor.getAttribute("href"));
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });

    // Add swipe gesture support
    let startX = 0;
    let endX = 0;

    document.addEventListener("touchstart", (event) => {
      startX = event.touches[0].clientX;
    });

    document.addEventListener("touchend", (event) => {
      endX = event.changedTouches[0].clientX;
      const deltaX = endX - startX;

      // Trigger navigation gestures
      if (deltaX > 50) {
        // Swipe right (open navigation menu)
        const navMenu = document.querySelector(".navigation-menu");
        if (navMenu) navMenu.classList.add("open");
      } else if (deltaX < -50) {
        // Swipe left (close navigation menu)
        const navMenu = document.querySelector(".navigation-menu");
        if (navMenu) navMenu.classList.remove("open");
      }
    });
  }
};

// Function to handle dynamic resizing
const handleDynamicResizing = () => {
  window.addEventListener("resize", () => {
    if (window.innerWidth < 768) {
      optimizeLayoutForMobile();
    } else {
      document.body.classList.remove("mobile-optimized");
    }
  });
};

// Initialize mobile optimization
const initializeMobileOptimization = () => {
  optimizeLayoutForMobile();
  enableLazyLoading();
  enhanceTouchExperience();
  handleDynamicResizing();
};

// Wait for DOM to fully load before initializing
document.addEventListener("DOMContentLoaded", () => {
  initializeMobileOptimization();
});
