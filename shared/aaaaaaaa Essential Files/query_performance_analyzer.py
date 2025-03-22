import time
import logging
from typing import Callable, Dict, Any, List
from shared.utils import log_info, log_error, format_execution_time
from shared.config import SUPPORTED_SOCIAL_MEDIA_PLATFORMS, QUERY_LOG_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"{QUERY_LOG_PATH}/query_performance.log"),
    ],
)

class QueryPerformanceAnalyzer:
    def __init__(self):
        self.supported_platforms = SUPPORTED_SOCIAL_MEDIA_PLATFORMS

    def analyze_query_performance(
        self,
        query_function: Callable[..., Any],
        query_args: Dict[str, Any],
        repeat: int = 1,
    ) -> Dict[str, Any]:
        """
        Analyze the performance of a given query function.

        Args:
            query_function: The function to execute.
            query_args: Arguments to pass to the query function.
            repeat: Number of times to repeat the execution for averaging.

        Returns:
            A dictionary containing performance metrics.
        """
        execution_times = []
        results = None

        try:
            for _ in range(repeat):
                start_time = time.perf_counter()
                results = query_function(**query_args)
                execution_time = time.perf_counter() - start_time
                execution_times.append(execution_time)

            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)

            metrics = {
                "average_execution_time": avg_time,
                "max_execution_time": max_time,
                "min_execution_time": min_time,
                "results_count": len(results) if isinstance(results, list) else 1,
            }

            log_info(
                f"Query executed {repeat} times. "
                f"Avg: {format_execution_time(avg_time)}, "
                f"Max: {format_execution_time(max_time)}, "
                f"Min: {format_execution_time(min_time)}."
            )
            return metrics
        except Exception as e:
            log_error(f"Error analyzing query performance: {str(e)}")
            return {"error": str(e)}

    def log_query_metrics(
        self, platform: str, query: str, metrics: Dict[str, Any]
    ) -> None:
        """
        Log the performance metrics of a query for a specific platform.

        Args:
            platform: The name of the platform.
            query: The query that was executed.
            metrics: Performance metrics from `analyze_query_performance`.
        """
        try:
            if platform not in self.supported_platforms:
                log_error(f"Platform {platform} is not supported.")
                return

            log_info(
                f"Performance Metrics for {platform}:\n"
                f"Query: {query}\n"
                f"Average Execution Time: {format_execution_time(metrics['average_execution_time'])}\n"
                f"Max Execution Time: {format_execution_time(metrics['max_execution_time'])}\n"
                f"Min Execution Time: {format_execution_time(metrics['min_execution_time'])}\n"
                f"Results Count: {metrics['results_count']}\n"
            )
        except Exception as e:
            log_error(f"Error logging query metrics: {str(e)}")

    def monitor_platform_queries(
        self,
        platforms: List[str],
        query_function: Callable[..., Any],
        query_args: Dict[str, Any],
        repeat: int = 1,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Monitor and analyze queries across multiple platforms.

        Args:
            platforms: List of platforms to analyze queries for.
            query_function: The function to execute for queries.
            query_args: Arguments to pass to the query function.
            repeat: Number of times to repeat each query.

        Returns:
            A dictionary containing metrics for each platform.
        """
        platform_metrics = {}

        for platform in platforms:
            if platform not in self.supported_platforms:
                log_error(f"Platform {platform} is not supported.")
                continue

            query_args["platform"] = platform
            metrics = self.analyze_query_performance(
                query_function, query_args, repeat
            )
            platform_metrics[platform] = metrics
            self.log_query_metrics(platform, query_args.get("query", ""), metrics)

        return platform_metrics

# Example usage
if __name__ == "__main__":
    def example_query_function(platform: str, query: str) -> List[Dict[str, Any]]:
        """
        Simulated query function for demonstration purposes.
        Replace this with actual query logic.
        """
        time.sleep(0.5)  # Simulate query processing time
        return [{"id": 1, "content": f"Result for {query} on {platform}"}]

    analyzer = QueryPerformanceAnalyzer()

    platforms = ["Facebook", "Instagram", "Twitter", "LinkedIn", "TikTok", "YouTube"]
    query_args = {"query": "AI Technology"}

    metrics = analyzer.monitor_platform_queries(
        platforms, example_query_function, query_args, repeat=5
    )
    print("Query Performance Metrics:", metrics)
