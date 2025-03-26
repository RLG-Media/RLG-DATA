// dashboard.js

import axios from 'axios';
import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import {
  initializeApp,
  fetchPlatformAnalytics,
  createProject,
  startScraping,
} from './app';
import { handleNotifications, handleRealTimeUpdates } from './notifications';
import ChartComponent from './ChartComponent';

// Dashboard Component
const Dashboard = () => {
  const dispatch = useDispatch();
  const [analyticsData, setAnalyticsData] = useState({});
  const [projectData, setProjectData] = useState({ name: '', keywords: '' });
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [platform, setPlatform] = useState('OnlyFans');
  const [chartData, setChartData] = useState({});

  // Fetch analytics data on page load and when platform changes
  useEffect(() => {
    dispatch(initializeApp());
    loadPlatformAnalytics();
  }, [platform]);

  useEffect(() => {
    // Update chart data every time analyticsData updates
    if (analyticsData.engagementRate) {
      const updatedChartData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr'],
        datasets: [
          {
            label: 'Engagement Rate',
            data: [15, 25, 18, analyticsData.engagementRate],
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
          },
        ],
      };
      setChartData(updatedChartData);
    }
  }, [analyticsData]);

  // Load analytics data for selected platform
  const loadPlatformAnalytics = async () => {
    try {
      const data = await dispatch(fetchPlatformAnalytics(platform));
      setAnalyticsData(data.payload);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  // Handle project creation
  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      await dispatch(createProject(projectData));
      alert('Project created successfully!');
      setProjectData({ name: '', keywords: '' });
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Failed to create project.');
    }
  };

  // Handle scraping initiation
  const handleStartScraping = async (e) => {
    e.preventDefault();
    if (!scrapeUrl) {
      alert('Please enter a URL to scrape.');
      return;
    }
    try {
      await dispatch(startScraping(scrapeUrl));
      alert('Scraping started. You will be notified when complete.');
      setScrapeUrl('');
    } catch (error) {
      console.error('Error starting scraping:', error);
      alert('Scraping initiation failed.');
    }
  };

  // Platform selection for analytics
  const handlePlatformChange = (e) => {
    setPlatform(e.target.value);
  };

  return (
    <div className="dashboard-container">
      <div className="analytics-section">
        <h2>{platform} Analytics</h2>
        <select onChange={handlePlatformChange} value={platform}>
          <option value="OnlyFans">OnlyFans</option>
          <option value="Fansly">Fansly</option>
          <option value="Patreon">Patreon</option>
          <option value="FanCentro">FanCentro</option>
          {/* Add other platforms as needed */}
        </select>
        <div className="analytics-content">
          {analyticsData ? (
            <div>
              <p>Followers: {analyticsData.followers}</p>
              <p>Engagement Rate: {analyticsData.engagementRate}%</p>
              <p>Top Content: {analyticsData.topContent}</p>
              <p>Revenue: ${analyticsData.revenue}</p>
            </div>
          ) : (
            <p>Loading analytics...</p>
          )}
        </div>
        <ChartComponent chartData={chartData} chartType="line" options={{ title: { display: true, text: 'Monthly Engagement Rate' } }} />
      </div>

      <div className="project-section">
        <h2>Create New Project</h2>
        <form onSubmit={handleCreateProject}>
          <input
            type="text"
            placeholder="Project Name"
            value={projectData.name}
            onChange={(e) => setProjectData({ ...projectData, name: e.target.value })}
            required
          />
          <input
            type="text"
            placeholder="Keywords (comma-separated)"
            value={projectData.keywords}
            onChange={(e) => setProjectData({ ...projectData, keywords: e.target.value })}
            required
          />
          <button type="submit">Create Project</button>
        </form>
      </div>

      <div className="scrape-section">
        <h2>Initiate Scraping</h2>
        <form onSubmit={handleStartScraping}>
          <input
            type="text"
            placeholder="Enter URL to scrape"
            value={scrapeUrl}
            onChange={(e) => setScrapeUrl(e.target.value)}
            required
          />
          <button type="submit">Start Scraping</button>
        </form>
      </div>
    </div>
  );
};

export default Dashboard;
