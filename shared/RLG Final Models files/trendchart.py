import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

class TrendChart:
    def __init__(self, data, chart_type="line", title="Trend Chart", x_axis="Date", y_axis="Value", theme="seaborn"):
        """
        Initializes the TrendChart instance.
        
        Args:
            data (pd.DataFrame): A pandas DataFrame containing the data to visualize.
            chart_type (str): Type of chart (line, bar, scatter, etc.).
            title (str): Chart title.
            x_axis (str): Column name to use for the X-axis.
            y_axis (str): Column name to use for the Y-axis.
            theme (str): Theme for the chart (e.g., 'seaborn', 'plotly_dark').
        """
        self.data = data
        self.chart_type = chart_type
        self.title = title
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.theme = theme

        # Set theme
        if theme == "seaborn":
            sns.set_theme(style="whitegrid")
        elif theme == "plotly_dark":
            plt.style.use("dark_background")

    def validate_data(self):
        """Validates the data to ensure required columns exist."""
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame.")
        if self.x_axis not in self.data.columns or self.y_axis not in self.data.columns:
            raise ValueError(f"Columns '{self.x_axis}' and '{self.y_axis}' must exist in the data.")
    
    def preprocess_data(self):
        """Prepares the data for chart generation."""
        if self.x_axis.lower() == "date":
            self.data[self.x_axis] = pd.to_datetime(self.data[self.x_axis])
        self.data.sort_values(by=self.x_axis, inplace=True)

    def plot_matplotlib(self, save_path=None):
        """Generates a chart using Matplotlib."""
        self.validate_data()
        self.preprocess_data()

        plt.figure(figsize=(12, 6))
        if self.chart_type == "line":
            plt.plot(self.data[self.x_axis], self.data[self.y_axis], marker="o", label=self.title)
        elif self.chart_type == "bar":
            plt.bar(self.data[self.x_axis], self.data[self.y_axis], label=self.title)
        elif self.chart_type == "scatter":
            plt.scatter(self.data[self.x_axis], self.data[self.y_axis], label=self.title, alpha=0.7)
        else:
            raise ValueError(f"Unsupported chart type: {self.chart_type}")

        plt.title(self.title, fontsize=16)
        plt.xlabel(self.x_axis, fontsize=12)
        plt.ylabel(self.y_axis, fontsize=12)
        plt.legend()
        plt.grid(True)

        if save_path:
            plt.savefig(save_path)
        plt.show()

    def plot_seaborn(self):
        """Generates a chart using Seaborn."""
        self.validate_data()
        self.preprocess_data()

        plt.figure(figsize=(12, 6))
        if self.chart_type == "line":
            sns.lineplot(x=self.x_axis, y=self.y_axis, data=self.data)
        elif self.chart_type == "scatter":
            sns.scatterplot(x=self.x_axis, y=self.y_axis, data=self.data)
        elif self.chart_type == "bar":
            sns.barplot(x=self.x_axis, y=self.y_axis, data=self.data)
        else:
            raise ValueError(f"Unsupported chart type: {self.chart_type}")

        plt.title(self.title, fontsize=16)
        plt.xlabel(self.x_axis, fontsize=12)
        plt.ylabel(self.y_axis, fontsize=12)
        plt.show()

    def plot_plotly(self):
        """Generates an interactive chart using Plotly."""
        self.validate_data()
        self.preprocess_data()

        if self.chart_type == "line":
            fig = px.line(self.data, x=self.x_axis, y=self.y_axis, title=self.title)
        elif self.chart_type == "bar":
            fig = px.bar(self.data, x=self.x_axis, y=self.y_axis, title=self.title)
        elif self.chart_type == "scatter":
            fig = px.scatter(self.data, x=self.x_axis, y=self.y_axis, title=self.title)
        else:
            raise ValueError(f"Unsupported chart type: {self.chart_type}")

        fig.update_layout(template=self.theme)
        fig.show()

    def export_chart(self, file_path):
        """Exports the chart to a file."""
        self.validate_data()
        self.preprocess_data()
        self.plot_matplotlib(save_path=file_path)
        print(f"Chart saved to {file_path}.")

# Example Usage
if __name__ == "__main__":
    # Sample data
    sample_data = pd.DataFrame({
        "Date": [datetime(2025, 1, i) for i in range(1, 11)],
        "Value": [10, 12, 15, 14, 20, 25, 22, 30, 28, 35]
    })

    # Generate trend chart
    chart = TrendChart(
        data=sample_data,
        chart_type="line",
        title="Sample Trend Chart",
        x_axis="Date",
        y_axis="Value",
        theme="plotly_dark"
    )
    chart.plot_plotly()
