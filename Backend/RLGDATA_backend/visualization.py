import matplotlib.pyplot as plt
import io
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_mentions_graph(platforms, mentions):
    """
    Create a bar chart that visualizes the number of mentions across platforms.
    
    :param platforms: List of platform names (e.g., ['Twitter', 'Facebook', 'Instagram'])
    :param mentions: List of mention counts corresponding to the platforms (e.g., [120, 90, 150])
    :return: Base64-encoded image that can be embedded in HTML
    """
    try:
        # Ensure platforms and mentions are provided and match in length
        if len(platforms) != len(mentions):
            logging.error("Platforms and mentions lists are not the same length.")
            return None

        # Create the bar chart
        plt.figure(figsize=(8, 6))
        plt.bar(platforms, mentions, color='skyblue')
        plt.title('Mentions by Platform')
        plt.xlabel('Platform')
        plt.ylabel('Mentions')

        # Save the chart to a bytes object and encode it for rendering in HTML
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return 'data:image/png;base64,{}'.format(graph_url)

    except Exception as e:
        logging.error(f"Error generating mentions graph: {e}")
        return None


def create_sentiment_graph(labels, sizes, colors=None):
    """
    Create a pie chart that visualizes sentiment breakdown.
    
    :param labels: List of sentiment labels (e.g., ['Positive', 'Neutral', 'Negative'])
    :param sizes: List of sentiment percentages (e.g., [50, 30, 20])
    :param colors: Optional list of colors for each sentiment category
    :return: Base64-encoded image that can be embedded in HTML
    """
    try:
        # Default colors if none provided
        if colors is None:
            colors = ['#4CAF50', '#FFC107', '#F44336']  # Green, Yellow, Red for Positive, Neutral, Negative

        # Create the pie chart
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('Sentiment Breakdown')

        # Save the chart to a bytes object and encode it for rendering in HTML
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return 'data:image/png;base64,{}'.format(graph_url)

    except Exception as e:
        logging.error(f"Error generating sentiment graph: {e}")
        return None
