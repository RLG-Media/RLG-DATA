// charts.js

// Load Google Charts for additional chart types
google.charts.load('current', { packages: ['corechart', 'bar'] });

// Initialize charts when Google Charts library is loaded
google.charts.setOnLoadCallback(drawInitialCharts);

// Initialize Chart.js charts for real-time updates
let mentionsChart, sentimentChart, engagementChart;

// Utility to generate dynamic colors for charts
function generateDynamicColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(`hsl(${Math.floor((360 / count) * i)}, 70%, 50%)`);
    }
    return colors;
}

// Function to draw initial charts with default data
function drawInitialCharts() {
    drawMentionsChart();
    drawSentimentChart();
    drawEngagementChart();
}

// Mentions chart (Google Charts)
function drawMentionsChart() {
    const data = google.visualization.arrayToDataTable([
        ['Platform', 'Mentions'],
        ['Twitter', 120],
        ['Instagram', 150],
        ['Facebook', 100],
        ['YouTube', 70],
        ['TikTok', 90],
        ['OnlyFans', 130],
        ['FanCentro', 85]
    ]);

    const options = {
        title: 'Mentions by Platform',
        pieHole: 0.4,
        colors: generateDynamicColors(7),
        chartArea: { width: '90%', height: '75%' },
        fontSize: 14
    };

    const chart = new google.visualization.PieChart(document.getElementById('mentionsChart'));
    chart.draw(data, options);
}

// Sentiment analysis chart (Chart.js)
function drawSentimentChart() {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    sentimentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                label: 'Sentiment Analysis',
                data: [50, 30, 20],
                backgroundColor: ['#66BB6A', '#FFEE58', '#EF5350'],
                borderColor: ['#4CAF50', '#FFC107', '#F44336'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Count', font: { size: 14 } }
                },
                x: { title: { display: true, text: 'Sentiment', font: { size: 14 } } }
            },
            plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
            }
        }
    });
}

// Engagement over time chart (Chart.js)
function drawEngagementChart() {
    const ctx = document.getElementById('engagementChart').getContext('2d');
    engagementChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Engagement Rate',
                data: [20, 25, 30, 35],
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Rate (%)', font: { size: 14 } }
                },
                x: { title: { display: true, text: 'Time Period', font: { size: 14 } } }
            },
            plugins: {
                legend: { position: 'top' },
                tooltip: { enabled: true }
            }
        }
    });
}

// Function to update mentions chart data dynamically
function updateMentionsChart(data) {
    const googleData = google.visualization.arrayToDataTable([
        ['Platform', 'Mentions'],
        ...data.map(item => [item.platform, item.mentions])
    ]);

    const options = {
        title: 'Updated Mentions by Platform',
        pieHole: 0.4,
        colors: generateDynamicColors(data.length),
        chartArea: { width: '90%', height: '75%' },
        fontSize: 14
    };

    const chart = new google.visualization.PieChart(document.getElementById('mentionsChart'));
    chart.draw(googleData, options);
}

// Function to update sentiment chart data
function updateSentimentChart(data) {
    sentimentChart.data.datasets[0].data = data;
    sentimentChart.update();
}

// Function to update engagement chart data
function updateEngagementChart(data, labels) {
    engagementChart.data.labels = labels;
    engagementChart.data.datasets[0].data = data;
    engagementChart.update();
}

// Listen for real-time updates via WebSocket
socket.on('real_time_update', (update) => {
    if (update.chartType === 'mentions') {
        updateMentionsChart(update.data);
    } else if (update.chartType === 'sentiment') {
        updateSentimentChart(update.data);
    } else if (update.chartType === 'engagement') {
        updateEngagementChart(update.data.values, update.data.labels);
    }
});

// Function to fetch and update charts dynamically
async function fetchAndUpdateCharts() {
    try {
        const response = await fetch('/api/get_chart_data');
        const chartData = await response.json();

        if (chartData.mentions) updateMentionsChart(chartData.mentions);
        if (chartData.sentiment) updateSentimentChart(chartData.sentiment);
        if (chartData.engagement) updateEngagementChart(chartData.engagement.values, chartData.engagement.labels);
    } catch (error) {
        console.error('Error fetching chart data:', error);
    }
}

// Call fetchAndUpdateCharts to initialize charts with live data
fetchAndUpdateCharts();

// Auto-resize charts on window resize
window.addEventListener('resize', drawInitialCharts);

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
