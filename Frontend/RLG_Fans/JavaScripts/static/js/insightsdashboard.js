// Insights Dashboard Module
class InsightsDashboard {
    constructor(config) {
      /**
       * Initialize the Insights Dashboard.
       *
       * @param {Object} config - Configuration options for the dashboard.
       * @param {string} config.apiEndpoint - API endpoint to fetch insights data.
       * @param {Array} config.widgets - Array of widget configurations.
       * @param {string} config.containerSelector - Selector for the dashboard container.
       */
      this.apiEndpoint = config.apiEndpoint;
      this.widgets = config.widgets || [];
      this.container = document.querySelector(config.containerSelector);
  
      if (!this.container) {
        throw new Error(`Invalid container selector: ${config.containerSelector}`);
      }
  
      this.init();
    }
  
    async init() {
      /**
       * Initialize the dashboard by fetching data and rendering widgets.
       */
      try {
        const data = await this.fetchData();
        this.renderWidgets(data);
        this.addEventListeners();
      } catch (error) {
        console.error('Failed to initialize the dashboard:', error);
        this.container.innerHTML = `<div class="error">Failed to load insights. Please try again later.</div>`;
      }
    }
  
    async fetchData() {
      /**
       * Fetch insights data from the API.
       *
       * @returns {Object} The fetched data.
       */
      const response = await fetch(this.apiEndpoint);
      if (!response.ok) {
        throw new Error('Failed to fetch insights data.');
      }
      return await response.json();
    }
  
    renderWidgets(data) {
      /**
       * Render the widgets on the dashboard using the fetched data.
       *
       * @param {Object} data - The insights data to populate the widgets.
       */
      this.container.innerHTML = ''; // Clear existing content
  
      this.widgets.forEach((widgetConfig) => {
        const widgetData = data[widgetConfig.dataKey] || {};
        const widget = this.createWidget(widgetConfig, widgetData);
        this.container.appendChild(widget);
      });
    }
  
    createWidget(config, data) {
      /**
       * Create a widget element.
       *
       * @param {Object} config - Widget configuration.
       * @param {Object} data - Data for the widget.
       * @returns {HTMLElement} The widget element.
       */
      const widget = document.createElement('div');
      widget.classList.add('widget');
      widget.setAttribute('data-widget-id', config.id);
  
      const title = document.createElement('h3');
      title.textContent = config.title;
      widget.appendChild(title);
  
      const content = document.createElement('div');
      content.classList.add('widget-content');
      widget.appendChild(content);
  
      if (config.type === 'chart') {
        this.renderChart(content, config, data);
      } else if (config.type === 'table') {
        this.renderTable(content, config, data);
      } else if (config.type === 'stat') {
        this.renderStat(content, data);
      } else {
        content.textContent = 'Unsupported widget type';
      }
  
      return widget;
    }
  
    renderChart(container, config, data) {
      /**
       * Render a chart widget using Chart.js.
       *
       * @param {HTMLElement} container - Container for the chart.
       * @param {Object} config - Widget configuration.
       * @param {Object} data - Data for the chart.
       */
      const canvas = document.createElement('canvas');
      container.appendChild(canvas);
  
      new Chart(canvas, {
        type: config.chartType || 'line',
        data: {
          labels: data.labels || [],
          datasets: data.datasets || [],
        },
        options: config.options || {},
      });
    }
  
    renderTable(container, config, data) {
      /**
       * Render a table widget.
       *
       * @param {HTMLElement} container - Container for the table.
       * @param {Object} config - Widget configuration.
       * @param {Array} data - Data for the table.
       */
      const table = document.createElement('table');
      table.classList.add('insights-table');
  
      const thead = document.createElement('thead');
      const headerRow = document.createElement('tr');
      (config.columns || []).forEach((col) => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
      });
      thead.appendChild(headerRow);
      table.appendChild(thead);
  
      const tbody = document.createElement('tbody');
      (data.rows || []).forEach((row) => {
        const tr = document.createElement('tr');
        row.forEach((cell) => {
          const td = document.createElement('td');
          td.textContent = cell;
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
  
      container.appendChild(table);
    }
  
    renderStat(container, data) {
      /**
       * Render a stat widget.
       *
       * @param {HTMLElement} container - Container for the stat widget.
       * @param {Object} data - Data for the stat widget.
       */
      container.innerHTML = `
        <div class="stat-value">${data.value || 'N/A'}</div>
        <div class="stat-label">${data.label || ''}</div>
      `;
    }
  
    addEventListeners() {
      /**
       * Add global event listeners for the dashboard.
       */
      this.container.addEventListener('click', (event) => {
        const widget = event.target.closest('.widget');
        if (widget) {
          this.handleWidgetClick(widget.getAttribute('data-widget-id'));
        }
      });
    }
  
    handleWidgetClick(widgetId) {
      /**
       * Handle widget click events.
       *
       * @param {string} widgetId - The ID of the clicked widget.
       */
      console.log(`Widget clicked: ${widgetId}`);
      // Additional logic can be added here, such as opening a detailed view.
    }
  }
  
  // Example Usage
  document.addEventListener('DOMContentLoaded', () => {
    const insightsDashboard = new InsightsDashboard({
      apiEndpoint: '/api/insights',
      containerSelector: '#insightsDashboard',
      widgets: [
        {
          id: 'user-engagement',
          title: 'User Engagement',
          type: 'chart',
          chartType: 'bar',
          dataKey: 'userEngagement',
          options: { responsive: true },
        },
        {
          id: 'top-performers',
          title: 'Top Performers',
          type: 'table',
          columns: ['Name', 'Metric', 'Value'],
          dataKey: 'topPerformers',
        },
        {
          id: 'conversion-rate',
          title: 'Conversion Rate',
          type: 'stat',
          dataKey: 'conversionRate',
        },
      ],
    });
  });
  
  export default InsightsDashboard;
  