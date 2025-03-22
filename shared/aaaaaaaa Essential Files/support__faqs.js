// Support FAQs Script for RLG Data and RLG Fans
// This script provides interactivity for managing and searching FAQs.

document.addEventListener("DOMContentLoaded", () => {
    const faqContainer = document.querySelector("#faq-container");
    const searchInput = document.querySelector("#faq-search");
    const categoriesDropdown = document.querySelector("#faq-categories");
    const faqs = [];

    // Fetch FAQs from the backend
    async function fetchFAQs() {
        try {
            const response = await fetch("/api/faqs");
            const data = await response.json();
            faqs.push(...data); // Populate the FAQs array
            renderFAQs(faqs);
            populateCategories(faqs);
        } catch (error) {
            console.error("Failed to fetch FAQs:", error);
            faqContainer.innerHTML = `<p class='error'>Unable to load FAQs. Please try again later.</p>`;
        }
    }

    // Render FAQs in the container
    function renderFAQs(faqsToRender) {
        faqContainer.innerHTML = "";
        if (faqsToRender.length === 0) {
            faqContainer.innerHTML = `<p class='no-results'>No FAQs found.</p>`;
            return;
        }
        faqsToRender.forEach(faq => {
            const faqElement = document.createElement("div");
            faqElement.className = "faq-item";
            faqElement.innerHTML = `
                <h3 class="faq-question">${faq.question}</h3>
                <div class="faq-answer hidden">${faq.answer}</div>
            `;
            faqElement.querySelector(".faq-question").addEventListener("click", () => {
                const answer = faqElement.querySelector(".faq-answer");
                answer.classList.toggle("hidden");
            });
            faqContainer.appendChild(faqElement);
        });
    }

    // Populate categories dropdown
    function populateCategories(faqs) {
        const categories = [...new Set(faqs.map(faq => faq.category))];
        categories.forEach(category => {
            const option = document.createElement("option");
            option.value = category;
            option.textContent = category;
            categoriesDropdown.appendChild(option);
        });
    }

    // Filter FAQs based on search query and category
    function filterFAQs() {
        const query = searchInput.value.toLowerCase();
        const selectedCategory = categoriesDropdown.value;
        const filteredFAQs = faqs.filter(faq => {
            const matchesQuery = faq.question.toLowerCase().includes(query) || faq.answer.toLowerCase().includes(query);
            const matchesCategory = selectedCategory === "all" || faq.category === selectedCategory;
            return matchesQuery && matchesCategory;
        });
        renderFAQs(filteredFAQs);
    }

    // Event listeners
    searchInput.addEventListener("input", filterFAQs);
    categoriesDropdown.addEventListener("change", filterFAQs);

    // Initial fetch
    fetchFAQs();

    // Accessibility Enhancements
    faqContainer.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            const target = event.target;
            if (target.classList.contains("faq-question")) {
                target.nextElementSibling.classList.toggle("hidden");
            }
        }
    });
});
