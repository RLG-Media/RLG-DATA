// d3_visualizations.js

// Define the dimensions and margins for the visualizations
const margin = { top: 20, right: 30, bottom: 50, left: 60 };
const width = 800 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

// Utility function to make charts responsive
function makeResponsive(svg) {
    svg.attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        .attr("preserveAspectRatio", "xMidYMid meet");
}

// Function to create a trending engagement line chart
function createEngagementLineChart(data) {
    const svg = d3.select("#engagement-line-chart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    makeResponsive(svg);

    // Define x and y scales
    const x = d3.scaleTime()
        .domain(d3.extent(data, d => new Date(d.date)))
        .range([0, width]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.engagement)])
        .range([height, 0]);

    // Add x and y axes
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(6).tickFormat(d3.timeFormat("%b %d")))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    svg.append("g")
        .call(d3.axisLeft(y));

    // Add line path
    const line = d3.line()
        .x(d => x(new Date(d.date)))
        .y(d => y(d.engagement))
        .curve(d3.curveMonotoneX);

    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "#007bff")
        .attr("stroke-width", 2)
        .attr("d", line);

    // Add tooltips
    const tooltip = d3.select("#engagement-line-chart")
        .append("div")
        .style("position", "absolute")
        .style("background", "#fff")
        .style("padding", "5px")
        .style("border", "1px solid #ccc")
        .style("border-radius", "4px")
        .style("display", "none");

    svg.selectAll(".dot")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", d => x(new Date(d.date)))
        .attr("cy", d => y(d.engagement))
        .attr("r", 4)
        .attr("fill", "#007bff")
        .on("mouseover", (event, d) => {
            tooltip.style("display", "block")
                .html(`Date: ${d.date}<br>Engagement: ${d.engagement}`)
                .style("left", `${event.pageX + 10}px`)
                .style("top", `${event.pageY - 20}px`);
        })
        .on("mouseout", () => tooltip.style("display", "none"));
}

// Function to create a pie chart for monetization type distribution
function createMonetizationPieChart(data) {
    const radius = Math.min(width, height) / 2 - margin.top;

    const svg = d3.select("#monetization-pie-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`);

    makeResponsive(svg);

    const color = d3.scaleOrdinal()
        .domain(data.map(d => d.type))
        .range(d3.schemeTableau10);

    const pie = d3.pie().value(d => d.amount);
    const arc = d3.arc().innerRadius(0).outerRadius(radius);

    // Draw the pie chart
    svg.selectAll("path")
        .data(pie(data))
        .enter()
        .append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.type))
        .attr("stroke", "#fff")
        .style("stroke-width", "2px")
        .on("mouseover", (event, d) => {
            d3.select(event.target).style("opacity", 0.8);
        })
        .on("mouseout", (event, d) => {
            d3.select(event.target).style("opacity", 1);
        });

    // Add legends
    const legend = svg.append("g")
        .attr("transform", `translate(${-(width / 2) + 20}, ${-(height / 2) + 20})`);

    legend.selectAll("rect")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", 0)
        .attr("y", (d, i) => i * 20)
        .attr("width", 15)
        .attr("height", 15)
        .attr("fill", d => color(d.type));

    legend.selectAll("text")
        .data(data)
        .enter()
        .append("text")
        .attr("x", 20)
        .attr("y", (d, i) => i * 20 + 12)
        .text(d => d.type)
        .style("font-size", "12px")
        .attr("alignment-baseline", "middle");
}

// Real-time data updates via WebSocket
const socket = io.connect();

socket.on("update_engagement_data", (newData) => {
    d3.select("#engagement-line-chart").select("svg").remove();
    createEngagementLineChart(newData);
});

socket.on("update_monetization_data", (newData) => {
    d3.select("#monetization-pie-chart").select("svg").remove();
    createMonetizationPieChart(newData);
});

// Fetch initial data
async function fetchInitialData() {
    try {
        const response = await fetch("/api/get_visualization_data");
        const { engagementData, monetizationData } = await response.json();

        createEngagementLineChart(engagementData);
        createMonetizationPieChart(monetizationData);
    } catch (error) {
        console.error("Error fetching initial data:", error);
    }
}

// Call to fetch and render initial data
fetchInitialData();

<script src="https://d3js.org/d3.v7.min.js"></script>
