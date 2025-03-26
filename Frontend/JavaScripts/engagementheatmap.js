// Import D3.js library
import * as d3 from 'd3';

// EngagementHeatmap class
class EngagementHeatmap {
  constructor(config) {
    /**
     * Initializes the heatmap instance.
     *
     * @param {Object} config - Configuration object for the heatmap.
     * @param {string} config.selector - DOM selector for the heatmap container.
     * @param {Array} config.data - Array of data objects [{ day, hour, value }, ...].
     * @param {Array} config.days - Labels for the y-axis (days of the week).
     * @param {Array} config.hours - Labels for the x-axis (hours of the day).
     * @param {Object} config.colors - Configuration for the color scale.
     * @param {Object} config.tooltip - Tooltip configuration.
     */
    this.selector = config.selector;
    this.data = config.data || [];
    this.days = config.days || ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    this.hours = config.hours || Array.from({ length: 24 }, (_, i) => `${i}:00`);
    this.colors = config.colors || { min: '#ffffff', max: '#ff4500' };
    this.tooltip = config.tooltip || { enabled: true, formatter: d => `Value: ${d.value}` };

    this.margin = { top: 40, right: 20, bottom: 40, left: 70 };
    this.width = 800;
    this.height = 400;
  }

  render() {
    /**
     * Renders the heatmap in the specified container.
     */
    const { selector, data, days, hours, colors, tooltip, margin, width, height } = this;

    // Validate container
    const container = d3.select(selector);
    if (container.empty()) {
      throw new Error(`Invalid selector: ${selector}`);
    }

    // Clear any existing content
    container.html('');

    // SVG canvas setup
    const svg = container
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Scales
    const xScale = d3.scaleBand().domain(hours).range([0, width]).padding(0.05);
    const yScale = d3.scaleBand().domain(days).range([0, height]).padding(0.05);
    const colorScale = d3
      .scaleSequential(d3.interpolateRgb(colors.min, colors.max))
      .domain(d3.extent(data, d => d.value));

    // Axes
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);

    svg.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(xAxis)
      .selectAll('text')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end');

    svg.append('g').call(yAxis);

    // Heatmap cells
    const cells = svg
      .selectAll('rect')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => xScale(d.hour))
      .attr('y', d => yScale(d.day))
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', d => colorScale(d.value))
      .attr('stroke', '#ccc');

    // Tooltip
    if (tooltip.enabled) {
      const tooltipDiv = d3
        .select('body')
        .append('div')
        .attr('class', 'heatmap-tooltip')
        .style('position', 'absolute')
        .style('background', '#fff')
        .style('padding', '8px')
        .style('border', '1px solid #ddd')
        .style('border-radius', '4px')
        .style('pointer-events', 'none')
        .style('opacity', 0);

      cells.on('mouseover', (event, d) => {
        tooltipDiv
          .html(tooltip.formatter(d))
          .style('left', `${event.pageX + 10}px`)
          .style('top', `${event.pageY - 20}px`)
          .style('opacity', 1);
      });

      cells.on('mouseout', () => {
        tooltipDiv.style('opacity', 0);
      });
    }
  }
}

// Example usage
document.addEventListener('DOMContentLoaded', () => {
  const sampleData = [
    { day: 'Monday', hour: '10:00', value: 30 },
    { day: 'Monday', hour: '11:00', value: 50 },
    { day: 'Tuesday', hour: '10:00', value: 70 },
    { day: 'Tuesday', hour: '11:00', value: 90 },
    // Add more data points here
  ];

  const heatmap = new EngagementHeatmap({
    selector: '#engagementHeatmap',
    data: sampleData,
    tooltip: {
      enabled: true,
      formatter: d => `Engagement: ${d.value}`,
    },
    colors: { min: '#ffffff', max: '#ff4500' },
  });

  heatmap.render();
});

export default EngagementHeatmap;
