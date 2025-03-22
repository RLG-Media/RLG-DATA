<template>
  <div class="analytics">
    <div class="analytics-header">
      <h2>Analytics Dashboard</h2>
      <p>Track your performance metrics and insights in real-time.</p>
    </div>

    <!-- Key Metrics Section -->
    <div class="metrics">
      <div class="metric" v-for="metric in keyMetrics" :key="metric.id">
        <div class="metric-icon">
          <i :class="metric.icon"></i>
        </div>
        <div class="metric-info">
          <h3>{{ metric.value }}</h3>
          <p>{{ metric.label }}</p>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts">
      <h3>Performance Charts</h3>
      <div class="chart-container">
        <LineChart
          :data="lineChartData"
          :options="lineChartOptions"
          class="chart"
        />
      </div>
      <div class="chart-container">
        <BarChart
          :data="barChartData"
          :options="barChartOptions"
          class="chart"
        />
      </div>
    </div>

    <!-- Data Table -->
    <div class="data-table">
      <h3>Detailed Analytics</h3>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Visitors</th>
            <th>Page Views</th>
            <th>Conversions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in tableData" :key="row.date">
            <td>{{ row.date }}</td>
            <td>{{ row.visitors }}</td>
            <td>{{ row.pageViews }}</td>
            <td>{{ row.conversions }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import LineChart from "@/components/charts/LineChart.vue";
import BarChart from "@/components/charts/BarChart.vue";

export default {
  name: "Analytics",
  components: {
    LineChart,
    BarChart,
  },
  data() {
    return {
      keyMetrics: [
        {
          id: 1,
          label: "Total Visitors",
          value: "12,345",
          icon: "fas fa-users",
        },
        {
          id: 2,
          label: "Page Views",
          value: "67,890",
          icon: "fas fa-chart-bar",
        },
        {
          id: 3,
          label: "Conversions",
          value: "1,234",
          icon: "fas fa-shopping-cart",
        },
        {
          id: 4,
          label: "Revenue",
          value: "$12,345",
          icon: "fas fa-dollar-sign",
        },
      ],
      lineChartData: {
        labels: ["January", "February", "March", "April", "May", "June"],
        datasets: [
          {
            label: "Visitors",
            data: [3000, 5000, 7000, 8000, 11000, 13000],
            borderColor: "#007bff",
            backgroundColor: "rgba(0, 123, 255, 0.1)",
          },
        ],
      },
      lineChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true },
        },
      },
      barChartData: {
        labels: ["Product A", "Product B", "Product C", "Product D"],
        datasets: [
          {
            label: "Sales",
            data: [5000, 7000, 3000, 8000],
            backgroundColor: ["#007bff", "#28a745", "#ffc107", "#dc3545"],
          },
        ],
      },
      barChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true },
        },
      },
      tableData: [
        { date: "2024-01-01", visitors: 1200, pageViews: 3500, conversions: 50 },
        { date: "2024-01-02", visitors: 1400, pageViews: 4200, conversions: 65 },
        { date: "2024-01-03", visitors: 1300, pageViews: 3900, conversions: 55 },
        { date: "2024-01-04", visitors: 1500, pageViews: 4600, conversions: 70 },
      ],
    };
  },
};
</script>

<style scoped>
.analytics {
  padding: 20px;
}

.analytics-header {
  text-align: center;
  margin-bottom: 20px;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.metric {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  margin-right: 15px;
  font-size: 2rem;
  color: #007bff;
}

.metric-info h3 {
  margin: 0;
  font-size: 1.5rem;
}

.metric-info p {
  margin: 0;
  color: #6c757d;
}

.charts {
  margin-bottom: 20px;
}

.chart-container {
  margin-bottom: 20px;
  height: 300px;
}

.data-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.data-table th,
.data-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.data-table th {
  background: #f8f9fa;
  font-weight: bold;
}

.data-table tbody tr:hover {
  background: #f1f3f5;
}
</style>
