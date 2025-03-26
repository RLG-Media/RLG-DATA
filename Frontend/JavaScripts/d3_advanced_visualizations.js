// d3_advanced_visualizations.js

// Ensure compatibility with older browsers
(function (d3) {
    "use strict";
  
    if (!d3) {
      console.error("D3 library is required but not loaded.");
      return;
    }
  
    /**
     * Create a responsive chart container.
     * @param {string} selector - DOM selector for the chart container.
     * @param {Object} margins - Margins for the chart.
     * @returns {Object} Dimensions for the chart.
     */
    function createChartContainer(selector, margins = { top: 20, right: 30, bottom: 40, left: 50 }) {
      const container = d3.select(selector);
      const width = parseInt(container.style("width")) - margins.left - margins.right;
      const height = parseInt(container.style("height")) - margins.top - margins.bottom;
  
      const svg = container
        .append("svg")
        .attr("width", width + margins.left + margins.right)
        .attr("height", height + margins.top + margins.bottom)
        .append("g")
        .attr("transform", `translate(${margins.left},${margins.top})`);
  
      return { svg, width, height };
    }
  
    /**
     * Generate a line chart.
     * @param {string} selector - DOM selector for the chart container.
     * @param {Array} data - Dataset to visualize.
     * @param {Object} options - Configuration options for the chart.
     */
    function createLineChart(selector, data, options = {}) {
      const { svg, width, height } = createChartContainer(selector, options.margins);
      const xScale = d3.scaleTime().domain(d3.extent(data, d => d.date)).range([0, width]);
      const yScale = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).range([height, 0]);
  
      // Axes
      svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(xScale));
      svg.append("g").call(d3.axisLeft(yScale));
  
      // Line generator
      const line = d3
        .line()
        .x(d => xScale(d.date))
        .y(d => yScale(d.value))
        .curve(d3.curveMonotoneX);
  
      // Draw line
      svg.append("path").datum(data).attr("fill", "none").attr("stroke", options.lineColor || "steelblue")
        .attr("stroke-width", 2).attr("d", line);
  
      // Tooltip
      const tooltip = d3.select("body").append("div").style("position", "absolute").style("padding", "8px")
        .style("background", "rgba(0, 0, 0, 0.7)").style("color", "white").style("border-radius", "4px")
        .style("pointer-events", "none").style("display", "none");
  
      svg.selectAll("dot")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", d => xScale(d.date))
        .attr("cy", d => yScale(d.value))
        .attr("r", 4)
        .attr("fill", options.dotColor || "red")
        .on("mouseover", (event, d) => {
          tooltip.style("display", "block").html(`Date: ${d.date}<br>Value: ${d.value}`);
        })
        .on("mousemove", event => {
          tooltip.style("top", `${event.pageY + 5}px`).style("left", `${event.pageX + 5}px`);
        })
        .on("mouseout", () => {
          tooltip.style("display", "none");
        });
    }
  
    /**
     * Generate a bar chart.
     * @param {string} selector - DOM selector for the chart container.
     * @param {Array} data - Dataset to visualize.
     * @param {Object} options - Configuration options for the chart.
     */
    function createBarChart(selector, data, options = {}) {
      const { svg, width, height } = createChartContainer(selector, options.margins);
      const xScale = d3.scaleBand().domain(data.map(d => d.label)).range([0, width]).padding(0.1);
      const yScale = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).range([height, 0]);
  
      // Axes
      svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(xScale));
      svg.append("g").call(d3.axisLeft(yScale));
  
      // Bars
      svg.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => xScale(d.label))
        .attr("y", d => yScale(d.value))
        .attr("width", xScale.bandwidth())
        .attr("height", d => height - yScale(d.value))
        .attr("fill", options.barColor || "teal")
        .on("mouseover", (event, d) => {
          tooltip.style("display", "block").html(`Label: ${d.label}<br>Value: ${d.value}`);
        })
        .on("mousemove", event => {
          tooltip.style("top", `${event.pageY + 5}px`).style("left", `${event.pageX + 5}px`);
        })
        .on("mouseout", () => {
          tooltip.style("display", "none");
        });
    }
  
    /**
     * Generate a pie chart.
     * @param {string} selector - DOM selector for the chart container.
     * @param {Array} data - Dataset to visualize.
     * @param {Object} options - Configuration options for the chart.
     */
    function createPieChart(selector, data, options = {}) {
      const { svg, width, height } = createChartContainer(selector, options.margins);
      const radius = Math.min(width, height) / 2;
  
      const colorScale = d3.scaleOrdinal().domain(data.map(d => d.label)).range(d3.schemeCategory10);
  
      const pie = d3.pie().value(d => d.value);
      const arc = d3.arc().innerRadius(0).outerRadius(radius);
  
      svg.attr("transform", `translate(${width / 2},${height / 2})`);
  
      svg.selectAll("path")
        .data(pie(data))
        .enter()
        .append("path")
        .attr("d", arc)
        .attr("fill", d => colorScale(d.data.label))
        .attr("stroke", "white")
        .style("stroke-width", "2px");
  
      // Add Labels
      svg.selectAll("text")
        .data(pie(data))
        .enter()
        .append("text")
        .text(d => `${d.data.label} (${d.data.value})`)
        .attr("transform", d => `translate(${arc.centroid(d)})`)
        .style("text-anchor", "middle")
        .style("font-size", "10px");
    }
  
    // Expose chart functions globally
    window.d3Visualizations = {
      createLineChart,
      createBarChart,
      createPieChart
    };
  })(d3);
  