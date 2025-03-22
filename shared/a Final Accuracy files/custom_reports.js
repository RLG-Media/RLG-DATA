document.addEventListener("DOMContentLoaded", () => {
    const filtersForm = document.getElementById("report-filters-form");
    const reportListContainer = document.querySelector(".report-list");
    const generateButton = document.querySelector(".generate-btn");

    // Utility function to create DOM elements
    const createElement = (tag, attributes = {}, innerHTML = "") => {
        const element = document.createElement(tag);
        for (let key in attributes) {
            element.setAttribute(key, attributes[key]);
        }
        element.innerHTML = innerHTML;
        return element;
    };

    // Fetch and display existing reports
    const fetchReports = async () => {
        try {
            const response = await fetch("/api/reports");
            if (!response.ok) throw new Error("Failed to fetch reports.");

            const reports = await response.json();
            renderReports(reports);
        } catch (error) {
            console.error("Error fetching reports:", error);
            reportListContainer.innerHTML = `<p class="error">Error loading reports. Please try again later.</p>`;
        }
    };

    // Render report items in the report list
    const renderReports = (reports) => {
        reportListContainer.innerHTML = "";
        if (reports.length === 0) {
            reportListContainer.innerHTML = `<p class="no-reports">No reports available. Please generate a new report.</p>`;
            return;
        }

        reports.forEach(report => {
            const reportItem = createElement("div", { class: "report-item" });

            const title = createElement("h3", {}, report.title);
            const generatedOn = createElement("p", {}, `Generated on: <span>${report.generated_on}</span>`);
            const downloadButton = createElement("a", { href: report.download_url, class: "download-btn" }, `<i class="fas fa-download"></i> Download`);

            reportItem.appendChild(title);
            reportItem.appendChild(generatedOn);
            reportItem.appendChild(downloadButton);
            reportListContainer.appendChild(reportItem);
        });
    };

    // Handle report generation
    const generateReport = async () => {
        try {
            const reportData = {
                report_type: document.getElementById("report-type").value,
                start_date: document.getElementById("start-date").value,
                end_date: document.getElementById("end-date").value,
                platform: document.getElementById("platform").value
            };

            const response = await fetch("/api/reports", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(reportData)
            });

            if (!response.ok) throw new Error("Failed to generate report.");

            const newReport = await response.json();
            alert("Report generated successfully!");
            fetchReports();
        } catch (error) {
            console.error("Error generating report:", error);
            alert("Error generating report. Please try again later.");
        }
    };

    // Handle form submission to apply filters
    filtersForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            const formData = new FormData(filtersForm);
            const queryString = new URLSearchParams(formData).toString();

            const response = await fetch(`/api/reports?${queryString}`);
            if (!response.ok) throw new Error("Failed to fetch filtered reports.");

            const filteredReports = await response.json();
            renderReports(filteredReports);
        } catch (error) {
            console.error("Error applying filters:", error);
            alert("Error applying filters. Please try again later.");
        }
    });

    // Event listener for the generate button
    generateButton.addEventListener("click", generateReport);

    // Initial fetch of reports on page load
    fetchReports();
});
