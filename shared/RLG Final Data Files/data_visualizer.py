"""
data_visualizer.py

This module provides data visualization functions for both RLG Data and RLG Fans.
It uses Plotly to create interactive visualizations that can be embedded in dashboards
or served as standalone HTML pages.

Features:
- Visualize RLG Data sentiment distribution as a pie chart.
- Visualize RLG Fans engagement distribution as a histogram with a box plot.
- Generate a combined dashboard with both visualizations.
- Robust logging and error handling.
- Region-aware and scalable for future enhancements.
"""

import os
import logging
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

# Set up logging
logger = logging.getLogger("DataVisualizer")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class DataVisualizer:
    def __init__(self, output_dir="visualizations"):
        """
        Initialize the DataVisualizer.

        Parameters:
            output_dir (str): Directory where generated visualization HTML files are saved.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        logger.info(f"DataVisualizer initialized. Output directory: {self.output_dir}")

    def visualize_rlg_data(self, data):
        """
        Visualize RLG Data metrics (e.g., media sentiment) using a pie chart.

        Parameters:
            data (dict): Dictionary containing RLG Data metrics.
                Expected format:
                    {
                        "articles": [
                            {"title": "Article 1", "sentiment": "positive"},
                            {"title": "Article 2", "sentiment": "negative"},
                            ...
                        ]
                    }
        Returns:
            str: File path of the saved HTML visualization, or None on failure.
        """
        logger.info("Starting visualization for RLG Data.")
        articles = data.get("articles", [])
        if not articles:
            logger.warning("No article data provided for RLG Data visualization.")
            return None

        # Create DataFrame and ensure 'sentiment' column exists.
        df = pd.DataFrame(articles)
        if "sentiment" not in df.columns:
            logger.warning("No 'sentiment' key found in articles; defaulting all values to 'neutral'.")
            df["sentiment"] = "neutral"

        # Calculate sentiment distribution.
        sentiment_counts = df["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["sentiment", "count"]

        # Create an interactive pie chart.
        fig = px.pie(sentiment_counts, names="sentiment", values="count",
                     title="RLG Data Sentiment Distribution",
                     color_discrete_sequence=px.colors.qualitative.Pastel)

        output_path = os.path.join(self.output_dir, "rlg_data_visualization.html")
        try:
            fig.write_html(output_path)
            logger.info(f"RLG Data visualization saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving RLG Data visualization: {e}")
            return None

    def visualize_rlg_fans(self, data):
        """
        Visualize RLG Fans metrics (e.g., fan engagement) using a histogram with marginal box plot.

        Parameters:
            data (dict): Dictionary containing RLG Fans metrics.
                Expected format:
                    {
                        "fans": [
                            {"content": "Post 1", "engagement": 50},
                            {"content": "Post 2", "engagement": 30},
                            ...
                        ]
                    }
        Returns:
            str: File path of the saved HTML visualization, or None on failure.
        """
        logger.info("Starting visualization for RLG Fans.")
        fans = data.get("fans", [])
        if not fans:
            logger.warning("No fan data provided for RLG Fans visualization.")
            return None

        df = pd.DataFrame(fans)
        if "engagement" not in df.columns:
            logger.warning("No 'engagement' key found in fan data; defaulting all values to 0.")
            df["engagement"] = 0

        # Create an interactive histogram.
        fig = px.histogram(df, x="engagement", nbins=20,
                           title="RLG Fans Engagement Distribution",
                           labels={"engagement": "Engagement Score"},
                           marginal="box",
                           color_discrete_sequence=px.colors.qualitative.Vivid)

        output_path = os.path.join(self.output_dir, "rlg_fans_visualization.html")
        try:
            fig.write_html(output_path)
            logger.info(f"RLG Fans visualization saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving RLG Fans visualization: {e}")
            return None

    def generate_combined_dashboard(self, rlg_data, rlg_fans):
        """
        Generate a combined dashboard that includes both RLG Data and RLG Fans visualizations.

        Parameters:
            rlg_data (dict): Data for RLG Data visualization.
            rlg_fans (dict): Data for RLG Fans visualization.

        Returns:
            str: File path of the saved combined dashboard HTML, or None on failure.
        """
        logger.info("Generating combined dashboard for RLG Data and RLG Fans.")

        # Prepare individual figures.
        data_fig = None
        fans_fig = None

        try:
            # Prepare RLG Data figure.
            articles = rlg_data.get("articles", [])
            if articles:
                df_data = pd.DataFrame(articles)
                if "sentiment" not in df_data.columns:
                    df_data["sentiment"] = "neutral"
                sentiment_counts = df_data["sentiment"].value_counts().reset_index()
                sentiment_counts.columns = ["sentiment", "count"]
                data_fig = px.pie(sentiment_counts, names="sentiment", values="count",
                                  title="RLG Data Sentiment Distribution",
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
            else:
                logger.warning("No RLG Data available for combined dashboard.")

            # Prepare RLG Fans figure.
            fans = rlg_fans.get("fans", [])
            if fans:
                df_fans = pd.DataFrame(fans)
                if "engagement" not in df_fans.columns:
                    df_fans["engagement"] = 0
                fans_fig = px.histogram(df_fans, x="engagement", nbins=20,
                                        title="RLG Fans Engagement Distribution",
                                        labels={"engagement": "Engagement Score"},
                                        marginal="box",
                                        color_discrete_sequence=px.colors.qualitative.Vivid)
            else:
                logger.warning("No RLG Fans data available for combined dashboard.")

            # Determine number of subplots.
            num_rows = sum(fig is not None for fig in [data_fig, fans_fig])
            if num_rows == 0:
                logger.error("No data available to generate the combined dashboard.")
                return None

            # Create a subplot dashboard.
            dashboard_fig = make_subplots(rows=num_rows, cols=1,
                                          subplot_titles=(
                                              (["RLG Data Sentiment Distribution"] if data_fig is not None else []) +
                                              (["RLG Fans Engagement Distribution"] if fans_fig is not None else [])
                                          ))
            current_row = 1
            if data_fig is not None:
                for trace in data_fig.data:
                    dashboard_fig.add_trace(trace, row=current_row, col=1)
                current_row += 1
            if fans_fig is not None:
                for trace in fans_fig.data:
                    dashboard_fig.add_trace(trace, row=current_row, col=1)

            dashboard_fig.update_layout(height=800, title_text="Combined Dashboard: RLG Data and RLG Fans")
            output_path = os.path.join(self.output_dir, "combined_dashboard.html")
            dashboard_fig.write_html(output_path)
            logger.info(f"Combined dashboard saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating combined dashboard: {e}")
            return None

if __name__ == "__main__":
    # For standalone testing, define sample data for RLG Data and RLG Fans.
    sample_rlg_data = {
        "articles": [
            {"title": "Article 1", "sentiment": "positive"},
            {"title": "Article 2", "sentiment": "negative"},
            {"title": "Article 3", "sentiment": "neutral"},
            {"title": "Article 4", "sentiment": "positive"},
        ]
    }
    sample_rlg_fans = {
        "fans": [
            {"content": "Great post!", "engagement": 50},
            {"content": "Not bad", "engagement": 30},
            {"content": "Awesome!", "engagement": 70},
            {"content": "Could be better", "engagement": 20},
        ]
    }

    visualizer = DataVisualizer()
    data_viz_path = visualizer.visualize_rlg_data(sample_rlg_data)
    fans_viz_path = visualizer.visualize_rlg_fans(sample_rlg_fans)
    dashboard_path = visualizer.generate_combined_dashboard(sample_rlg_data, sample_rlg_fans)

    print(f"RLG Data Visualization saved at: {data_viz_path}")
    print(f"RLG Fans Visualization saved at: {fans_viz_path}")
    print(f"Combined Dashboard saved at: {dashboard_path}")
