// data_fetcher.js

// Base API URLs for RLG Data and RLG Fans
const API_BASE_URLS = {
    rlgData: '/api/rlg_data',
    rlgFans: '/api/rlg_fans'
};

// Utility function to fetch data from a given endpoint
async function fetchData(endpoint, tool = 'rlgData') {
    try {
        const response = await fetch(`${API_BASE_URLS[tool]}${endpoint}`);
        if (!response.ok) {
            throw new Error(`Error fetching data from ${tool}: ${response.statusText}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Data fetching error:', error);
        return null;
    }
}

// Fetch mentions data for both tools
async function getMentionsData() {
    const rlgDataMentions = await fetchData('/mentions', 'rlgData');
    const rlgFansMentions = await fetchData('/mentions', 'rlgFans');
    return { rlgDataMentions, rlgFansMentions };
}

// Fetch sentiment data for both tools
async function getSentimentData() {
    const rlgDataSentiment = await fetchData('/sentiment', 'rlgData');
    const rlgFansSentiment = await fetchData('/sentiment', 'rlgFans');
    return { rlgDataSentiment, rlgFansSentiment };
}

// Fetch engagement data for both tools
async function getEngagementData() {
    const rlgDataEngagement = await fetchData('/engagement', 'rlgData');
    const rlgFansEngagement = await fetchData('/engagement', 'rlgFans');
    return { rlgDataEngagement, rlgFansEngagement };
}

// General data fetch function with a type selector
async function fetchToolData(dataType) {
    switch (dataType) {
        case 'mentions':
            return await getMentionsData();
        case 'sentiment':
            return await getSentimentData();
        case 'engagement':
            return await getEngagementData();
        default:
            console.warn(`Unknown data type: ${dataType}`);
            return null;
    }
}

// Example usage to populate charts
async function updateCharts() {
    const mentionsData = await fetchToolData('mentions');
    if (mentionsData) {
        updateMentionsChart(mentionsData.rlgDataMentions, mentionsData.rlgFansMentions);
    }

    const sentimentData = await fetchToolData('sentiment');
    if (sentimentData) {
        updateSentimentChart(sentimentData.rlgDataSentiment, sentimentData.rlgFansSentiment);
    }

    const engagementData = await fetchToolData('engagement');
    if (engagementData) {
        updateEngagementChart(engagementData.rlgDataEngagement, engagementData.rlgFansEngagement);
    }
}

// Export functions to make them accessible to other scripts
export { fetchToolData, updateCharts };
