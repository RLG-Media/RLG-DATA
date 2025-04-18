import logging
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("filters.log"),
        logging.StreamHandler()
    ]
)

class FilterEngine:
    """
    A versatile filtering engine for applying filters to datasets.
    """

    def __init__(self):
        self.custom_filters: Dict[str, Callable] = {}
        logging.info("FilterEngine initialized.")

    # --- Add Custom Filters ---
    def register_custom_filter(self, name: str, function: Callable):
        """
        Registers a custom filter function.
        :param name: Name of the custom filter.
        :param function: Callable implementing the filter logic.
        """
        self.custom_filters[name] = function
        logging.info(f"Custom filter registered: {name}")

    # --- Generic Filters ---
    def apply_filters(
        self,
        data: List[Dict[str, Any]],
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Applies filters, sorting, and pagination to a dataset.
        :param data: List of dictionaries representing the dataset.
        :param filters: Dictionary of filter criteria.
        :param sort_by: Key to sort by.
        :param sort_order: Sorting order ('asc' or 'desc').
        :param page: Page number for pagination.
        :param page_size: Number of items per page.
        :return: Filtered, sorted, and paginated dataset.
        """
        try:
            logging.info("Applying filters...")
            # Apply attribute filters
            for key, value in filters.items():
                if key in self.custom_filters:
                    data = self.custom_filters[key](data, value)
                else:
                    data = [item for item in data if self._default_filter(item, key, value)]

            # Apply sorting
            if sort_by:
                reverse = sort_order == "desc"
                data = sorted(data, key=lambda x: x.get(sort_by, None), reverse=reverse)

            # Apply pagination
            if page is not None and page_size is not None:
                start = (page - 1) * page_size
                end = start + page_size
                data = data[start:end]

            logging.info("Filters applied successfully.")
            return data
        except Exception as e:
            logging.error(f"Error applying filters: {e}")
            return []

    # --- Default Filter Logic ---
    @staticmethod
    def _default_filter(item: Dict[str, Any], key: str, value: Any) -> bool:
        """
        Default filtering logic for a key-value pair.
        :param item: Dictionary representing a data item.
        :param key: Key to filter by.
        :param value: Value or condition to filter with.
        :return: True if the item matches the filter; otherwise False.
        """
        if key not in item:
            return False

        item_value = item[key]
        if isinstance(value, (list, tuple)):
            return item_value in value
        elif isinstance(value, dict):
            # Range filters
            min_val = value.get("min")
            max_val = value.get("max")
            return (min_val is None or item_value >= min_val) and (max_val is None or item_value <= max_val)
        else:
            return item_value == value

    # --- Utility Filters ---
    @staticmethod
    def date_filter(data: List[Dict[str, Any]], date_key: str, date_range: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Filters data based on a date range.
        :param data: List of dictionaries representing the dataset.
        :param date_key: Key containing date values.
        :param date_range: Dictionary with 'start' and 'end' keys for date range.
        :return: Filtered dataset.
        """
        try:
            start_date = datetime.strptime(date_range["start"], "%Y-%m-%d") if "start" in date_range else None
            end_date = datetime.strptime(date_range["end"], "%Y-%m-%d") if "end" in date_range else None

            def date_in_range(item):
                date_value = datetime.strptime(item.get(date_key, ""), "%Y-%m-%d")
                return (start_date is None or date_value >= start_date) and \
                       (end_date is None or date_value <= end_date)

            return [item for item in data if date_in_range(item)]
        except Exception as e:
            logging.error(f"Error in date filter: {e}")
            return []

    @staticmethod
    def keyword_filter(data: List[Dict[str, Any]], keyword_key: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Filters data based on keywords.
        :param data: List of dictionaries representing the dataset.
        :param keyword_key: Key to search keywords in.
        :param keywords: List of keywords to match.
        :return: Filtered dataset.
        """
        try:
            return [item for item in data if any(kw.lower() in str(item.get(keyword_key, "")).lower() for kw in keywords)]
        except Exception as e:
            logging.error(f"Error in keyword filter: {e}")
            return []

# --- Example Usage ---
if __name__ == "__main__":
    dataset = [
        {"id": 1, "name": "Product A", "price": 100, "date_added": "2023-01-15"},
        {"id": 2, "name": "Product B", "price": 200, "date_added": "2023-02-20"},
        {"id": 3, "name": "Service A", "price": 150, "date_added": "2023-03-10"},
        {"id": 4, "name": "Service B", "price": 300, "date_added": "2023-04-05"}
    ]

    filter_engine = FilterEngine()

    # Register custom filters
    filter_engine.register_custom_filter("date_range", FilterEngine.date_filter)
    filter_engine.register_custom_filter("keywords", FilterEngine.keyword_filter)

    # Apply filters
    filters = {
        "price": {"min": 100, "max": 200},
        "date_range": {"date_key": "date_added", "date_range": {"start": "2023-01-01", "end": "2023-03-01"}}
    }

    filtered_data = filter_engine.apply_filters(
        dataset,
        filters=filters,
        sort_by="price",
        sort_order="asc",
        page=1,
        page_size=2
    )
    print("Filtered Data:", filtered_data)
