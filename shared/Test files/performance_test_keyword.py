import time
import tracemalloc
from seo_insights import SEOInsights

class PerformanceTestSEOInsights:
    """
    A class for performance testing the SEOInsights class.
    """

    def __init__(self):
        self.seo_tool = SEOInsights()
        self.sample_keyword = "digital marketing"
        self.sample_domain = "example.com"

    def measure_execution_time(self, method, *args, **kwargs):
        """
        Measures the execution time of a method.
        """
        start_time = time.time()
        method(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return elapsed_time

    def measure_memory_usage(self, method, *args, **kwargs):
        """
        Measures memory usage of a method.
        """
        tracemalloc.start()
        method(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {"current_memory": current, "peak_memory": peak}

    def performance_test_get_search_volume(self):
        """
        Performance test for get_search_volume method.
        """
        print("Testing get_search_volume method...")
        time_taken = self.measure_execution_time(self.seo_tool.get_search_volume, self.sample_keyword)
        memory_usage = self.measure_memory_usage(self.seo_tool.get_search_volume, self.sample_keyword)
        print(f"Execution Time: {time_taken:.2f} seconds")
        print(f"Memory Usage: {memory_usage['current_memory'] / 1024:.2f} KB (current), {memory_usage['peak_memory'] / 1024:.2f} KB (peak)")

    def performance_test_get_competitors(self):
        """
        Performance test for get_competitors method.
        """
        print("Testing get_competitors method...")
        time_taken = self.measure_execution_time(self.seo_tool.get_competitors, self.sample_keyword)
        memory_usage = self.measure_memory_usage(self.seo_tool.get_competitors, self.sample_keyword)
        print(f"Execution Time: {time_taken:.2f} seconds")
        print(f"Memory Usage: {memory_usage['current_memory'] / 1024:.2f} KB (current), {memory_usage['peak_memory'] / 1024:.2f} KB (peak)")

    def performance_test_fetch_website_traffic(self):
        """
        Performance test for fetch_website_traffic method.
        """
        print("Testing fetch_website_traffic method...")
        time_taken = self.measure_execution_time(self.seo_tool.fetch_website_traffic, self.sample_domain)
        memory_usage = self.measure_memory_usage(self.seo_tool.fetch_website_traffic, self.sample_domain)
        print(f"Execution Time: {time_taken:.2f} seconds")
        print(f"Memory Usage: {memory_usage['current_memory'] / 1024:.2f} KB (current), {memory_usage['peak_memory'] / 1024:.2f} KB (peak)")

    def performance_test_analyze_keyword_strength(self):
        """
        Performance test for analyze_keyword_strength method.
        """
        print("Testing analyze_keyword_strength method...")
        time_taken = self.measure_execution_time(self.seo_tool.analyze_keyword_strength, self.sample_keyword)
        memory_usage = self.measure_memory_usage(self.seo_tool.analyze_keyword_strength, self.sample_keyword)
        print(f"Execution Time: {time_taken:.2f} seconds")
        print(f"Memory Usage: {memory_usage['current_memory'] / 1024:.2f} KB (current), {memory_usage['peak_memory'] / 1024:.2f} KB (peak)")

    def run_all_tests(self):
        """
        Run all performance tests.
        """
        print("Starting performance tests...\n")
        self.performance_test_get_search_volume()
        print("\n")
        self.performance_test_get_competitors()
        print("\n")
        self.performance_test_fetch_website_traffic()
        print("\n")
        self.performance_test_analyze_keyword_strength()
        print("\nAll tests completed.")


if __name__ == "__main__":
    tester = PerformanceTestSEOInsights()
    tester.run_all_tests()
