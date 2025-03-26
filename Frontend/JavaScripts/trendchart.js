// Import required libraries (if using a module bundler like Webpack)
import Chart from 'chart.js/auto'; // For Chart.js
import * as d3 from 'd3'; // For D3.js (optional)

// TrendChart class
class TrendChart {
  constructor(config) {
    /**
     * Initializes the TrendChart instance.
     *
     * @param {Object} config - Configuration object for the trend chart.
     * @param {string} config.selector - DOM selector for the chart container.
     * @param {Array} config.labels - Labels for the x-axis (e.g., dates or categories).
     * @param {Array} config.data - Data points for the y-axis.
     * @param {string} config.type - Chart type ('line', 'bar', 'scatter').
     * @param {Object} config.options - Additional options for the chart.
     */
    this.selector = config.selector;
    this.labels = config.labels || [];
    this.data = config.data || [];
    this.type = config.type || 'line';
    this.options = config.options || {};
    this.chartInstance = null;
  }

  validateConfig() {
    /**
     * Validates the configuration.
     */
    if (!this.selector) {
      throw new Error('A valid selector is required to render the chart.');
    }
    if (!Array.isArray(this.labels) || !Array.isArray(this.data)) {
      throw new Error('Labels and data must be arrays.');
    }
    if (this.labels.length !== this.data.length) {
      throw new Error('Labels and data arrays must have the same length.');
    }
  }

  generateChart() {
    /**
     * Generates the trend chart using Chart.js.
     */
    this.validateConfig();

    const ctx = document.querySelector(this.selector).getContext('2d');
    this.chartInstance = new Chart(ctx, {
      type: this.type,
      data: {
        labels: this.labels,
        datasets: [
          {
            label: this.options.label || 'Trend Data',
            data: this.data,
            borderColor: this.options.borderColor || 'rgba(75, 192, 192, 1)',
            backgroundColor: this.options.backgroundColor || 'rgba(75, 192, 192, 0.2)',
            borderWidth: this.options.borderWidth || 2,
            pointRadius: this.options.pointRadius || 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: this.options.displayLegend || true,
          },
          tooltip: {
            enabled: true,
            mode: 'nearest',
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: this.options.xAxisLabel || 'X-Axis',
            },
          },
          y: {
            title: {
              display: true,
              text: this.options.yAxisLabel || 'Y-Axis',
            },
            beginAtZero: true,
          },
        },
      },
    });
  }

  updateChart(newData, newLabels) {
    /**
     * Updates the chart with new data and labels.
     *
     * @param {Array} newData - Updated data points.
     * @param {Array} newLabels - Updated labels for the x-axis.
     */
    if (!this.chartInstance) {
      throw new Error('Chart instance does not exist. Generate the chart first.');
    }

    this.chartInstance.data.labels = newLabels;
    this.chartInstance.data.datasets[0].data = newData;
    this.chartInstance.update();
  }

  destroyChart() {
    /**
     * Destroys the chart instance to free up resources.
     */
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
  }
}

// Example Usage
document.addEventListener('DOMContentLoaded', () => {
  const chartConfig = {
    selector: '#trendChart', // Canvas ID
    labels: ['January', 'February', 'March', 'April', 'May', 'June'],
    data: [10, 20, 15, 30, 25, 40],
    type: 'line',
    options: {
      label: 'Monthly Trends',
      borderColor: 'rgba(54, 162, 235, 1)',
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      xAxisLabel: 'Months',
      yAxisLabel: 'Values',
    },
  };

  const trendChart = new TrendChart(chartConfig);
  trendChart.generateChart();

  // Update the chart dynamically (optional)
  setTimeout(() => {
    trendChart.updateChart([15, 25, 20, 35, 30, 50], ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']);
  }, 5000);
});

export default TrendChart;
