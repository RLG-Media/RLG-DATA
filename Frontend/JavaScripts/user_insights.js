// user_insights.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './user_insights.css';

const UserInsights = ({ userId }) => {
    const [insightsData, setInsightsData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchUserInsights = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`/api/user_insights/${userId}`);
                setInsightsData(response.data);
            } catch (err) {
                setError("Failed to load user insights.");
            } finally {
                setLoading(false);
            }
        };
        fetchUserInsights();
    }, [userId]);

    if (loading) return <div className="loading-spinner">Loading Insights...</div>;
    if (error) return <div className="error-message">{error}</div>;

    return (
        <div className="user-insights-container">
            <h2>User Insights</h2>
            {insightsData ? (
                <div className="insights-content">
                    <div className="insight">
                        <h3>Total Engagement</h3>
                        <p>{insightsData.totalEngagement}</p>
                    </div>
                    <div className="insight">
                        <h3>Followers Gained</h3>
                        <p>{insightsData.followersGained}</p>
                    </div>
                    <div className="insight">
                        <h3>Top Performing Content</h3>
                        <p>{insightsData.topContent}</p>
                    </div>
                    <div className="insight">
                        <h3>Growth Rate</h3>
                        <p>{insightsData.growthRate}%</p>
                    </div>
                    <div className="insight">
                        <h3>Average Engagement Rate</h3>
                        <p>{insightsData.avgEngagementRate}%</p>
                    </div>
                </div>
            ) : (
                <div className="no-data-message">No insights available.</div>
            )}
        </div>
    );
};

export default UserInsights;
