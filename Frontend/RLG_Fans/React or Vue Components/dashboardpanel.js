// DashboardPanel.js

import React from 'react';
import { Card, Button } from 'react-bootstrap';
import ChartComponent from './ChartComponent';

const DashboardPanel = ({ stats, chartData }) => {
  return (
    <div className="dashboard-panel-container">
      <h2>RLG Fans Dashboard</h2>
      
      <div className="stats-cards">
        {/* Overview Cards */}
        <Card className="stat-card">
          <Card.Body>
            <Card.Title>Subscribers</Card.Title>
            <Card.Text>{stats.subscribers || 'Loading...'}</Card.Text>
          </Card.Body>
        </Card>

        <Card className="stat-card">
          <Card.Body>
            <Card.Title>Monthly Revenue</Card.Title>
            <Card.Text>${stats.revenue || 'Loading...'}</Card.Text>
          </Card.Body>
        </Card>

        <Card className="stat-card">
          <Card.Body>
            <Card.Title>New Followers</Card.Title>
            <Card.Text>{stats.newFollowers || 'Loading...'}</Card.Text>
          </Card.Body>
        </Card>
      </div>

      {/* Analytics Section */}
      <div className="analytics-section">
        <h3>Engagement & Growth Trends</h3>
        <ChartComponent 
          chartData={chartData} 
          chartType="line" 
          options={{ title: { display: true, text: 'Followers Growth Over Time' } }} 
        />
      </div>

      {/* Actions Section */}
      <div className="actions-section">
        <h3>Quick Actions</h3>
        <Button variant="primary" className="action-button" href="/create-project">Create New Project</Button>
        <Button variant="secondary" className="action-button" href="/analytics">View Analytics</Button>
        <Button variant="success" className="action-button" href="/settings">Settings</Button>
      </div>
    </div>
  );
};

export default DashboardPanel;
