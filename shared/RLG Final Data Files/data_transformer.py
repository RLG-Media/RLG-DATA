# data_transformer.py

import pandas as pd
from typing import List, Dict, Any

class DataTransformer:
    """
    A utility class for transforming raw data into standardized formats for RLG Data and RLG Fans.
    Supports normalization, aggregation, and formatting for visualization and reporting.
    """

    def __init__(self):
        pass

    @staticmethod
    def normalize_metrics(data: List[Dict[str, Any]], metric_keys: List[str]) -> List[Dict[str, Any]]:
        """
        Normalize selected metrics across different data sources.
        :param data: List of dictionaries containing raw data from various sources.
        :param metric_keys: List of metric keys to normalize.
        :return: Transformed list with normalized metrics.
        """
        transformed_data = []
        for item in data:
            normalized_item = {key: item.get(key, 0) for key in metric_keys}
            total = sum(normalized_item.values())
            if total > 0:
                normalized_item = {key: round(value / total, 2) for key, value in normalized_item.items()}
            transformed_item = {**item, **normalized_item}  # Merge original data with normalized metrics
            transformed_data.append(transformed_item)
        return transformed_data

    @staticmethod
    def aggregate_data(data: List[Dict[str, Any]], group_key: str, aggregation_fields: List[str]) -> pd.DataFrame:
        """
        Aggregate data by grouping based on a specified key and summing specified fields.
        :param data: List of dictionaries containing raw data.
        :param group_key: The key to group by (e.g., 'platform').
        :param aggregation_fields: List of fields to aggregate (e.g., ['mentions', 'engagement']).
        :return: Pandas DataFrame with aggregated data.
        """
        df = pd.DataFrame(data)
        aggregated_df = df.groupby(group_key)[aggregation_fields].sum().reset_index()
        return aggregated_df

    @staticmethod
    def format_for_chart(data: pd.DataFrame, x_key: str, y_keys: List[str]) -> Dict[str, List]:
        """
        Format data for charting by structuring x and y values.
        :param data: DataFrame containing data to plot.
        :param x_key: The x-axis key.
        :param y_keys: The y-axis keys.
        :return: Dictionary with lists for x and y values.
        """
        chart_data = {
            'x': data[x_key].tolist(),
            'y': {key: data[key].tolist() for key in y_keys}
        }
        return chart_data

    @staticmethod
    def clean_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean data by removing invalid entries and filling missing values.
        :param data: List of raw data dictionaries.
        :return: List of cleaned data dictionaries.
        """
        cleaned_data = []
        for entry in data:
            # Example: Remove entries with null or empty values in critical fields
            if all(entry.get(key) is not None for key in entry.keys()):
                cleaned_data.append(entry)
        return cleaned_data

    @staticmethod
    def calculate_growth(current_data: pd.DataFrame, previous_data: pd.DataFrame, key: str) -> pd.DataFrame:
        """
        Calculate growth metrics by comparing current and previous data.
        :param current_data: DataFrame containing the current period's data.
        :param previous_data: DataFrame containing the previous period's data.
        :param key: Key on which to join the data for growth comparison.
        :return: DataFrame with growth rates added.
        """
        combined = current_data.merge(previous_data, on=key, suffixes=('_current', '_previous'))
        for col in current_data.columns:
            if col != key:
                combined[f'{col}_growth'] = (
                    (combined[f'{col}_current'] - combined[f'{col}_previous']) / combined[f'{col}_previous']
                ).fillna(0).round(2)
        return combined[[key] + [col for col in combined.columns if 'growth' in col]]

# Example Usage
if __name__ == "__main__":
    # Sample data
    raw_data = [
        {'platform': 'Twitter', 'mentions': 150, 'engagement': 250},
        {'platform': 'Instagram', 'mentions': 300, 'engagement': 500},
        {'platform': 'Facebook', 'mentions': 100, 'engagement': 200}
    ]

    transformer = DataTransformer()
    normalized_data = transformer.normalize_metrics(raw_data, ['mentions', 'engagement'])
    aggregated_data = transformer.aggregate_data(raw_data, 'platform', ['mentions', 'engagement'])
    chart_data = transformer.format_for_chart(aggregated_data, 'platform', ['mentions', 'engagement'])

    print("Normalized Data:", normalized_data)
    print("Aggregated Data:\n", aggregated_data)
    print("Chart Data:", chart_data)
