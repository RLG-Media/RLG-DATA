// Brand Activation Script for RLG Data and RLG Fans

// Ensure DOM is fully loaded before executing scripts
document.addEventListener('DOMContentLoaded', function () {
    // Initialize functionality
    initializeBrandActivation();

    /**
     * Initializes the brand activation functionality by setting event listeners and loading existing data.
     */
    function initializeBrandActivation() {
        // Event listener for campaign form submission
        const campaignForm = document.getElementById('brand-activation-form');
        if (campaignForm) {
            campaignForm.addEventListener('submit', handleCampaignFormSubmit);
        }

        // Load active campaigns into the UI
        loadActiveCampaigns();

        // Load analytics for campaigns
        loadCampaignAnalytics();
    }

    /**
     * Handles the campaign creation form submission.
     * @param {Event} event The form submission event.
     */
    function handleCampaignFormSubmit(event) {
        event.preventDefault();

        // Extract form values
        const campaignName = document.getElementById('campaign-name').value.trim();
        const targetAudience = document.getElementById('target-audience').value.trim();
        const objectives = document.getElementById('objectives').value.trim();
        const budget = parseFloat(document.getElementById('budget').value);
        const channels = Array.from(document.getElementById('channels').selectedOptions).map(option => option.value);

        // Validation
        if (!campaignName || !targetAudience || !objectives || !budget || channels.length === 0) {
            alert('Please fill in all fields before submitting.');
            return;
        }

        // Create campaign object
        const newCampaign = {
            name: campaignName,
            targetAudience,
            objectives,
            budget,
            channels,
            createdAt: new Date().toISOString(),
            status: 'Pending',
        };

        // Send campaign data to backend
        fetch('/api/brand_activation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newCampaign)
        })
            .then(response => {
                if (!response.ok) throw new Error('Failed to create campaign.');
                return response.json();
            })
            .then(data => {
                alert('Campaign created successfully!');
                loadActiveCampaigns(); // Refresh the campaigns list
            })
            .catch(error => {
                console.error('Error creating campaign:', error);
                alert('An error occurred while creating the campaign. Please try again.');
            });
    }

    /**
     * Fetches and loads active campaigns from the backend into the UI.
     */
    function loadActiveCampaigns() {
        fetch('/api/active_campaigns')
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch campaigns.');
                return response.json();
            })
            .then(campaigns => {
                const container = document.getElementById('active-campaigns');
                container.innerHTML = '';

                if (campaigns.length === 0) {
                    container.innerHTML = '<p>No active campaigns yet. Start creating one now!</p>';
                    return;
                }

                campaigns.forEach(campaign => {
                    const campaignDiv = document.createElement('div');
                    campaignDiv.classList.add('campaign');

                    campaignDiv.innerHTML = `
                        <h3>${campaign.name}</h3>
                        <p><strong>Target Audience:</strong> ${campaign.targetAudience}</p>
                        <p><strong>Budget:</strong> $${campaign.budget}</p>
                        <p><strong>Status:</strong> ${campaign.status}</p>
                        <button class="btn-secondary view-analytics" data-campaign-id="${campaign.id}">View Analytics</button>
                    `;

                    container.appendChild(campaignDiv);
                });

                // Add event listeners for analytics buttons
                document.querySelectorAll('.view-analytics').forEach(button => {
                    button.addEventListener('click', function () {
                        const campaignId = this.getAttribute('data-campaign-id');
                        loadCampaignAnalytics(campaignId);
                    });
                });
            })
            .catch(error => {
                console.error('Error fetching campaigns:', error);
                const container = document.getElementById('active-campaigns');
                container.innerHTML = '<p>Failed to load campaigns. Please try again later.</p>';
            });
    }

    /**
     * Fetches and loads analytics for a specific campaign or provides an overview.
     * @param {string} [campaignId] Optional campaign ID to fetch detailed analytics.
     */
    function loadCampaignAnalytics(campaignId) {
        const endpoint = campaignId ? `/api/campaign_analytics/${campaignId}` : '/api/campaign_analytics';
        fetch(endpoint)
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch analytics.');
                return response.json();
            })
            .then(analytics => {
                const container = document.getElementById('campaign-analytics');
                container.innerHTML = '';

                if (campaignId) {
                    container.innerHTML = `
                        <h3>Analytics for Campaign: ${analytics.name}</h3>
                        <p><strong>Impressions:</strong> ${analytics.impressions}</p>
                        <p><strong>Clicks:</strong> ${analytics.clicks}</p>
                        <p><strong>Conversions:</strong> ${analytics.conversions}</p>
                    `;
                } else {
                    container.innerHTML = '<h3>Analytics Overview</h3>';
                    analytics.forEach(campaign => {
                        const campaignAnalytics = document.createElement('div');
                        campaignAnalytics.classList.add('analytics-summary');

                        campaignAnalytics.innerHTML = `
                            <h4>${campaign.name}</h4>
                            <p><strong>Impressions:</strong> ${campaign.impressions}</p>
                            <p><strong>Clicks:</strong> ${campaign.clicks}</p>
                            <p><strong>Conversions:</strong> ${campaign.conversions}</p>
                        `;

                        container.appendChild(campaignAnalytics);
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching analytics:', error);
                const container = document.getElementById('campaign-analytics');
                container.innerHTML = '<p>Failed to load analytics. Please try again later.</p>';
            });
    }
});
