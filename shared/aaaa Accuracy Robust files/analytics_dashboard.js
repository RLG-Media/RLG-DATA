// analytics_dashboard.js
// Script for handling dynamic analytics dashboard interactions and visualizations.

document.addEventListener("DOMContentLoaded", () => {
    console.log("Analytics Dashboard Loaded.");
  
    const apiUrl = "/api/analytics"; // Backend API endpoint for analytics data
    const dashboardContainer = document.getElementById("dashboard-container");
    const filterForm = document.getElementById("filter-form");
    const chartContainers = {
      userGrowth: document.getElementById("user-growth-chart"),
      engagementRates: document.getElementById("engagement-rates-chart"),
      platformBreakdown: document.getElementById("platform-breakdown-chart"),
    };
  
    // Helper function to fetch data from the API
    async function fetchData(endpoint, params = {}) {
      try {
        const query = new URLSearchParams(params).toString();
        const response = await fetch(`${endpoint}?${query}`);
        if (!response.ok) throw new Error("Network response was not ok");
        return await response.json();
      } catch (error) {
        console.error("Error fetching data:", error);
        alert("Failed to load analytics data. Please try again.");
      }
    }
  
    // Helper function to render charts
    function renderChart(container, data, type = "line", options = {}) {
      if (!container) {
        console.error("Invalid container for chart rendering.");
        return;
      }
  
      const ctx = container.getContext("2d");
      new Chart(ctx, {
        type: type,
        data: data,
        options: options,
      });
    }
  
    // Load analytics data and update dashboard
    async function loadDashboard(filters = {}) {
      try {
        const data = await fetchData(apiUrl, filters);
  
        // User Growth Chart
        renderChart(chartContainers.userGrowth, {
          labels: data.userGrowth.dates,
          datasets: [{
            label: "User Growth",
            data: data.userGrowth.values,
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            borderColor: "rgba(75, 192, 192, 1)",
            borderWidth: 1,
          }],
        });
  
        // Engagement Rates Chart
        renderChart(chartContainers.engagementRates, {
          labels: data.engagementRates.labels,
          datasets: [{
            label: "Engagement Rate",
            data: data.engagementRates.values,
            backgroundColor: "rgba(153, 102, 255, 0.2)",
            borderColor: "rgba(153, 102, 255, 1)",
            borderWidth: 1,
          }],
        });
  
        // Platform Breakdown Chart (Pie)
        renderChart(chartContainers.platformBreakdown, {
          labels: data.platformBreakdown.labels,
          datasets: [{
            label: "Platform Distribution",
            data: data.platformBreakdown.values,
            backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
          }],
        });
  
        console.log("Dashboard updated successfully.");
      } catch (error) {
        console.error("Error loading dashboard:", error);
      }
    }
  
    // Event Listener: Handle filter submission
    filterForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData(filterForm);
      const filters = Object.fromEntries(formData.entries());
      await loadDashboard(filters);
    });
  
    // Initialize Dashboard
    loadDashboard();
  });
  