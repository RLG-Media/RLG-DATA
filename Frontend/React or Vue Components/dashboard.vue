<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Welcome, {{ userName }}</h1>
      <p>Your analytics overview is ready.</p>
    </header>

    <section class="dashboard-metrics">
      <div class="metric-card" v-for="metric in metrics" :key="metric.id">
        <div class="card-header">
          <h2>{{ metric.title }}</h2>
        </div>
        <div class="card-body">
          <p class="metric-value">{{ metric.value }}</p>
          <p class="metric-description">{{ metric.description }}</p>
        </div>
      </div>
    </section>

    <section class="dashboard-content">
      <h2>Recent Activity</h2>
      <activity-feed :activities="recentActivities" />

      <h2>Performance Chart</h2>
      <performance-chart :data="performanceData" />
    </section>
  </div>
</template>

<script>
import ActivityFeed from "./components/ActivityFeed.vue";
import PerformanceChart from "./components/PerformanceChart.vue";

export default {
  name: "Dashboard",
  components: {
    ActivityFeed,
    PerformanceChart,
  },
  data() {
    return {
      userName: "User", // This should be dynamically fetched
      metrics: [
        { id: 1, title: "Revenue", value: "$12,450", description: "This month" },
        { id: 2, title: "New Subscribers", value: "342", description: "In the last 7 days" },
        { id: 3, title: "Engagement Rate", value: "74%", description: "Across all platforms" },
      ],
      recentActivities: [
        { id: 1, message: "New subscriber: John Doe", timestamp: "2 hours ago" },
        { id: 2, message: "Revenue goal achieved!", timestamp: "1 day ago" },
        { id: 3, message: "Campaign 'Spring Sale' launched", timestamp: "3 days ago" },
      ],
      performanceData: [
        { date: "2024-11-01", value: 300 },
        { date: "2024-11-02", value: 450 },
        { date: "2024-11-03", value: 500 },
        { date: "2024-11-04", value: 620 },
      ],
    };
  },
};
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  background-color: #f9f9f9;
  font-family: "Roboto", sans-serif;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  margin: 0;
  color: #333;
}

.dashboard-header p {
  font-size: 1.2rem;
  color: #777;
}

.dashboard-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
  flex: 1 1 calc(33.333% - 1rem);
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  text-align: center;
}

.metric-card .card-header h2 {
  font-size: 1.2rem;
  color: #444;
}

.metric-card .card-body .metric-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #3273dc;
}

.metric-card .card-body .metric-description {
  font-size: 0.9rem;
  color: #666;
}

.dashboard-content h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #333;
}
</style>
