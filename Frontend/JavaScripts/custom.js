// Real-time updates via WebSocket
var socket = io.connect(window.location.origin);

// Handle WebSocket connection events
socket.on('connect', function() {
    console.log('Connected to WebSocket');
});

socket.on('disconnect', function() {
    console.log('Disconnected from WebSocket');
});

// Handle real-time updates from backend
socket.on('message', function(data) {
    console.log('Real-time update:', data);
    if (data.update_type === 'mentions') {
        updateMentionsGraph(data);
    } else if (data.update_type === 'sentiment') {
        updateSentimentGraph(data);
    } else if (data.update_type === 'scrape_status') {
        showScrapeNotification(data);
    }
});

// Update mentions graph
function updateMentionsGraph(data) {
    const ctx = document.getElementById('mentionsGraph').getContext('2d');
    const mentionsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Mentions',
                data: data.values,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Update sentiment graph
function updateSentimentGraph(data) {
    const ctx = document.getElementById('sentimentGraph').getContext('2d');
    const sentimentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Sentiment',
                data: data.values,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Show scrape status notification
function showScrapeNotification(data) {
    const notification = document.createElement('div');
    notification.className = 'alert alert-info';
    notification.innerText = `Scrape status: ${data.status} for ${data.url}`;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

// Handle form submission for creating new projects
document.getElementById('createProjectForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const projectName = document.getElementById('projectName').value;
    const keywords = document.getElementById('keywords').value;

    fetch('/api/projects', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        body: JSON.stringify({ name: projectName, keywords: keywords })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Project created successfully') {
            alert('Project created!');
            window.location.reload();
        } else {
            alert(data.message || 'Error creating project.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error creating project.');
    });
});

// Handle real-time scraping notifications
function handleScrapeNotification() {
    const scrapeButton = document.getElementById('scrapeButton');
    scrapeButton.addEventListener('click', function() {
        const url = document.getElementById('scrapeUrl').value;

        if (!url || !isValidUrl(url)) {
            alert('Please enter a valid URL.');
            return;
        }

        fetch('/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ url: url })
        })
        .then(response => response.json())
        .then(data => {
            alert('Scraping started, please wait for results.');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error starting scraping.');
        });
    });
}

// Function to validate URL format
function isValidUrl(url) {
    const urlRegex = /^(ftp|http|https):\/\/[^ "]+$/;
    return urlRegex.test(url);
}

// Initialize scraping notification handling
handleScrapeNotification();

// Flash message timeout
setTimeout(function() {
    const flashMessage = document.querySelector('.flash-message');
    if (flashMessage) {
        flashMessage.style.display = 'none';
    }
}, 5000);

// Initialize Google Charts for any additional charts
google.charts.load('current', { packages: ['corechart'] });
google.charts.setOnLoadCallback(drawAdditionalCharts);

function drawAdditionalCharts() {
    const data = google.visualization.arrayToDataTable([
        ['Task', 'Hours per Day'],
        ['Work', 11],
        ['Eat', 2],
        ['Commute', 2],
        ['Watch TV', 2],
        ['Sleep', 7]
    ]);

    const options = {
        title: 'My Daily Activities',
        pieHole: 0.4
    };

    const chart = new google.visualization.PieChart(document.getElementById('piechart'));
    chart.draw(data, options);
}
