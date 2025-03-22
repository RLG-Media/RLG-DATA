/**
 * client_portal.js
 *
 * This script adds interactivity to the client portal for both RLG Data and RLG Fans.
 * It fetches updated data from the backend using the Fetch API and updates interactive charts,
 * as well as refreshing key metrics on the dashboard.
 *
 * Requirements:
 *  - Chart.js (or your preferred charting library) must be loaded in your HTML.
 *  - Your backend should expose endpoints returning JSON data for metrics and charts.
 *
 * Recommendations:
 *  - Customize polling intervals and error handling as needed.
 *  - Extend the API URLs to include region filters if necessary.
 *  - Enhance chart configuration and data formatting based on your requirements.
 */

const API_ENDPOINTS = {
    dataMetrics: "/api/data",   // Endpoint returning RLG Data metrics (JSON)
    fansMetrics: "/api/fans"    // Endpoint returning RLG Fans metrics (JSON)
  };
  
  // Polling interval in milliseconds (e.g., update every 60 seconds)
  const POLL_INTERVAL = 60000;
  
  // Global chart objects (to be initialized once)
  let dataChart, fansChart;
  
  // Initialize charts when the page loads
  document.addEventListener("DOMContentLoaded", () => {
    initializeCharts();
    refreshDashboard(); // Initial fetch on load
  
    // Set up polling to refresh dashboard data periodically
    setInterval(refreshDashboard, POLL_INTERVAL);
  });
  
  /**
   * Initializes the charts using Chart.js.
   * Assumes that <canvas> elements with IDs "dataChartCanvas" and "fansChartCanvas" exist.
   */
  function initializeCharts() {
    // Check if Chart.js is loaded
    if (typeof Chart === "undefined") {
      console.error("Chart.js is not loaded. Please include Chart.js in your HTML.");
      return;
    }
  
    // RLG Data Chart: For example, a pie chart for sentiment distribution.
    const dataCtx = document.getElementById("dataChartCanvas").getContext("2d");
    dataChart = new Chart(dataCtx, {
      type: "pie",
      data: {
        labels: ["Positive", "Neutral", "Negative"],
        datasets: [{
          data: [0, 0, 0],
          backgroundColor: ["#28a745", "#ffc107", "#dc3545"],
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "RLG Data Sentiment Distribution"
          }
        }
      }
    });
  
    // RLG Fans Chart: For example, a bar chart for fan engagement metrics.
    const fansCtx = document.getElementById("fansChartCanvas").getContext("2d");
    fansChart = new Chart(fansCtx, {
      type: "bar",
      data: {
        labels: ["Total Fans", "Active Today"],
        datasets: [{
          label: "Engagement Metrics",
          data: [0, 0],
          backgroundColor: ["#007bff", "#17a2b8"]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "RLG Fans Engagement Overview"
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
  
  /**
   * Fetches data from a given API endpoint.
   * @param {string} url - The API endpoint URL.
   * @returns {Promise<Object>} - A promise that resolves with the JSON data.
   */
  async function fetchData(url) {
    try {
      const response = await fetch(url, {
        credentials: "same-origin",
        headers: {
          "Accept": "application/json"
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const jsonData = await response.json();
      return jsonData;
    } catch (error) {
      console.error("Error fetching data from", url, error);
      return null;
    }
  }
  
  /**
   * Refreshes the dashboard by fetching new data and updating charts and metrics.
   */
  async function refreshDashboard() {
    console.info("Refreshing dashboard data...");
  
    // Fetch and update RLG Data metrics
    const dataMetrics = await fetchData(API_ENDPOINTS.dataMetrics);
    if (dataMetrics) {
      updateDataMetrics(dataMetrics);
      updateDataChart(dataMetrics);
    } else {
      console.error("Failed to fetch RLG Data metrics.");
    }
  
    // Fetch and update RLG Fans metrics
    const fansMetrics = await fetchData(API_ENDPOINTS.fansMetrics);
    if (fansMetrics) {
      updateFansMetrics(fansMetrics);
      updateFansChart(fansMetrics);
    } else {
      console.error("Failed to fetch RLG Fans metrics.");
    }
  }
  
  /**
   * Updates the RLG Data metrics section of the dashboard.
   * @param {Object} metrics - The metrics JSON data.
   */
  function updateDataMetrics(metrics) {
    // Example: Update inner text of elements with IDs matching metric keys.
    // Ensure your HTML contains these elements (e.g., <span id="totalMentions"></span>).
    if (metrics.total_mentions !== undefined) {
      document.getElementById("totalMentions").innerText = metrics.total_mentions;
    }
    if (metrics.positive !== undefined) {
      document.getElementById("positiveCount").innerText = metrics.positive;
    }
    if (metrics.neutral !== undefined) {
      document.getElementById("neutralCount").innerText = metrics.neutral;
    }
    if (metrics.negative !== undefined) {
      document.getElementById("negativeCount").innerText = metrics.negative;
    }
  }
  
  /**
   * Updates the RLG Data Chart with new sentiment distribution data.
   * @param {Object} metrics - The metrics JSON data.
   */
  function updateDataChart(metrics) {
    if (dataChart && metrics.positive !== undefined && metrics.neutral !== undefined && metrics.negative !== undefined) {
      dataChart.data.datasets[0].data = [metrics.positive, metrics.neutral, metrics.negative];
      dataChart.update();
    }
  }
  
  /**
   * Updates the RLG Fans metrics section of the dashboard.
   * @param {Object} metrics - The metrics JSON data.
   */
  function updateFansMetrics(metrics) {
    // Example: Update inner text of elements with IDs for fans metrics.
    if (metrics.total_fans !== undefined) {
      document.getElementById("totalFans").innerText = metrics.total_fans;
    }
    if (metrics.active_today !== undefined) {
      document.getElementById("activeToday").innerText = metrics.active_today;
    }
    if (metrics.growth_rate !== undefined) {
      document.getElementById("growthRate").innerText = metrics.growth_rate;
    }
  }
  
  /**
   * Updates the RLG Fans Chart with new engagement data.
   * @param {Object} metrics - The metrics JSON data.
   */
  function updateFansChart(metrics) {
    if (fansChart && metrics.total_fans !== undefined && metrics.active_today !== undefined) {
      fansChart.data.datasets[0].data = [metrics.total_fans, metrics.active_today];
      fansChart.update();
    }
  }
  
  /**
   * Additional utility functions or event listeners can be added here.
   * For example, you might add filtering controls, region selectors, or manual refresh buttons.
   */
  
  // End of client_portal.js
  