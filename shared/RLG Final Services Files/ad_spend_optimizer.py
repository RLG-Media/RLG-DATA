import logging
from typing import Dict, List
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# Configure logging: logs will be output to both a file and the console.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ad_spend_optimizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdSpendOptimizer:
    """
    A class to optimize advertising spend across platforms using ROI-based models.
    
    This class supports:
      - Training a Linear Regression model on historical ad spend data.
      - Recommending optimal budget allocations across platforms based on the trained model.
      - Evaluating campaign performance (ROI) based on actual spend versus performance metrics.
    
    The current implementation assumes data for five platforms:
      "facebook", "instagram", "twitter", "linkedin", and "tiktok".
    """
    
    def __init__(self):
        """
        Initializes the AdSpendOptimizer with a Linear Regression model and a StandardScaler.
        """
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        logger.info("AdSpendOptimizer initialized.")

    def fit_model(self, ad_data: List[Dict[str, float]], target_metric: str):
        """
        Fit the optimization model using historical ad spend and ROI data.
        
        Args:
            ad_data (List[Dict[str, float]]): Historical data where each entry is a dictionary
                with spend data for each platform and a target performance metric (e.g., "roi").
                Example entry:
                {
                    "facebook": 500,
                    "instagram": 300,
                    "twitter": 200,
                    "linkedin": 100,
                    "tiktok": 400,
                    "roi": 1.5
                }
            target_metric (str): The performance metric to optimize (e.g., "roi", "conversions").
        """
        try:
            spends = []
            metrics = []
            for entry in ad_data:
                # Collect spend data in a consistent order for each platform.
                spends.append([
                    entry.get("facebook", 0),
                    entry.get("instagram", 0),
                    entry.get("twitter", 0),
                    entry.get("linkedin", 0),
                    entry.get("tiktok", 0)
                ])
                metrics.append(entry.get(target_metric, 0))
            spends = np.array(spends)
            metrics = np.array(metrics)

            # Normalize spend data for better regression performance.
            spends_scaled = self.scaler.fit_transform(spends)
            self.model.fit(spends_scaled, metrics)
            logger.info("Ad spend optimization model trained successfully on target metric '%s'.", target_metric)
        except Exception as e:
            logger.error("Failed to train the ad spend optimization model: %s", e)
            raise

    def recommend_allocation(self, budget: float) -> Dict[str, float]:
        """
        Recommend an optimal ad spend allocation for a given budget.
        
        The model predicts a performance score from a given allocation; this implementation
        uses a baseline equal-allocation vector to derive allocation ratios.
        
        Args:
            budget (float): The total advertising budget.
        
        Returns:
            Dict[str, float]: Recommended budget allocation across platforms.
                Example:
                {
                    "facebook": 200.0,
                    "instagram": 180.0,
                    "twitter": 150.0,
                    "linkedin": 140.0,
                    "tiktok": 330.0
                }
        """
        try:
            # Use a baseline equal allocation (as a dummy vector) to simulate prediction.
            # This is a placeholder; more complex optimization logic may be needed.
            equal_allocation = np.ones((1, 5)) / 5  # Equal proportions across 5 platforms.
            equal_allocation_scaled = self.scaler.transform(equal_allocation)
            prediction = self.model.predict(equal_allocation_scaled)

            # To derive allocation ratios, we assume higher prediction means more efficient spend.
            # Here we use the predicted value as a baseline (this is a simplistic approach).
            # In practice, you might run optimization routines to maximize ROI given budget constraints.
            allocation_ratios = np.full((5,), 1.0 / 5)  # Start with equal ratios.
            # Optionally, adjust ratios based on model insights (this example does not modify the equal split).
            allocation = {
                "facebook": allocation_ratios[0] * budget,
                "instagram": allocation_ratios[1] * budget,
                "twitter": allocation_ratios[2] * budget,
                "linkedin": allocation_ratios[3] * budget,
                "tiktok": allocation_ratios[4] * budget,
            }
            logger.info("Recommended ad spend allocation calculated.")
            return allocation
        except Exception as e:
            logger.error("Failed to recommend ad spend allocation: %s", e)
            raise

    def evaluate_performance(self, spend_data: Dict[str, float], performance_data: Dict[str, float]) -> Dict[str, float]:
        """
        Evaluate the performance of the ad spend allocation.
        
        Calculates ROI for each platform based on actual spend and performance metrics.
        
        Args:
            spend_data (Dict[str, float]): Actual spend data across platforms.
            performance_data (Dict[str, float]): Performance metrics across platforms.
        
        Returns:
            Dict[str, float]: ROI per platform.
        """
        try:
            results = {}
            for platform, spend in spend_data.items():
                # Calculate ROI as performance metric divided by spend, handling zero spend gracefully.
                roi = performance_data.get(platform, 0) / spend if spend > 0 else 0
                results[platform] = roi
            logger.info("Performance evaluation completed: %s", results)
            return results
        except Exception as e:
            logger.error("Failed to evaluate performance: %s", e)
            raise

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. Real-time optimization: Integrate real-time performance feedback to dynamically adjust allocations.
# 2. A/B Testing: Consider an A/B testing framework to validate different allocation strategies.
# 3. Advanced Optimization: Explore nonlinear or multi-objective optimization models if linear regression proves insufficient.
# 4. Regional Adjustments: Incorporate region, country, city, or town-specific data if available.
# 5. Persistence: Log historical allocation recommendations and performance metrics for future analysis.

# -------------------------------
# Standalone Testing Example:
# -------------------------------
if __name__ == "__main__":
    optimizer = AdSpendOptimizer()

    # Example historical data for training the model.
    historical_data = [
        {"facebook": 500, "instagram": 300, "twitter": 200, "linkedin": 100, "tiktok": 400, "roi": 1.5},
        {"facebook": 400, "instagram": 400, "twitter": 300, "linkedin": 200, "tiktok": 300, "roi": 1.7},
        {"facebook": 600, "instagram": 500, "twitter": 300, "linkedin": 200, "tiktok": 400, "roi": 1.6},
    ]
    optimizer.fit_model(historical_data, "roi")
    
    # Recommend allocation for a $1000 budget.
    recommendations = optimizer.recommend_allocation(1000)
    print("Recommended Allocation:", recommendations)
    
    # Evaluate performance with sample spend and performance data.
    performance = optimizer.evaluate_performance(
        spend_data={"facebook": 200, "instagram": 200, "twitter": 200, "linkedin": 200, "tiktok": 200},
        performance_data={"facebook": 500, "instagram": 400, "twitter": 300, "linkedin": 200, "tiktok": 350}
    )
    print("Performance Evaluation:", performance)
