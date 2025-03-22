import re
from datetime import datetime
from typing import List, Dict, Any, Union
from utils import DatabaseConnection, DataSanitizer
from exceptions import SearchError


class AdvancedSearch:
    """
    A class for advanced search functionalities, including filtering, sorting,
    and full-text search across various data sources.
    """

    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize the AdvancedSearch class with a database connection.
        Args:
            db_connection (DatabaseConnection): A database connection instance.
        """
        self.db = db_connection

    def validate_query(self, query: Dict[str, Any]) -> None:
        """
        Validates the search query structure and content.
        Args:
            query (dict): The search query parameters.
        Raises:
            SearchError: If the query structure is invalid.
        """
        required_keys = {"keywords", "filters", "sort", "pagination"}
        if not required_keys.issubset(query.keys()):
            raise SearchError("Invalid query structure. Missing required keys.")
        if not isinstance(query["keywords"], str) or not query["keywords"].strip():
            raise SearchError("Keywords must be a non-empty string.")
        if not isinstance(query["filters"], dict):
            raise SearchError("Filters must be a dictionary.")
        if not isinstance(query["sort"], dict):
            raise SearchError("Sort must be a dictionary.")
        if not isinstance(query["pagination"], dict):
            raise SearchError("Pagination must be a dictionary.")

    def perform_search(
        self, query: Dict[str, Any], dataset: str
    ) -> Dict[str, Union[List[Dict[str, Any]], int]]:
        """
        Perform the search based on the provided query.
        Args:
            query (dict): The search query parameters.
            dataset (str): The dataset to search in.
        Returns:
            dict: Search results, including the data and total count.
        """
        self.validate_query(query)
        keywords = DataSanitizer.sanitize(query["keywords"])
        filters = query["filters"]
        sort = query["sort"]
        pagination = query["pagination"]

        # Build the search query
        search_conditions = self.build_conditions(keywords, filters)
        order_clause = self.build_sort_clause(sort)
        limit_clause = self.build_pagination_clause(pagination)

        # Perform the database query
        results, total_count = self.query_database(dataset, search_conditions, order_clause, limit_clause)

        return {"results": results, "total_count": total_count}

    def build_conditions(self, keywords: str, filters: Dict[str, Any]) -> str:
        """
        Build search conditions based on keywords and filters.
        Args:
            keywords (str): Search keywords.
            filters (dict): Search filters.
        Returns:
            str: SQL WHERE clause or equivalent.
        """
        conditions = []

        # Full-text search on keywords
        if keywords:
            conditions.append(f"FULLTEXT MATCH(content) AGAINST('{keywords}')")

        # Add filter conditions
        for field, value in filters.items():
            if isinstance(value, list):
                sanitized_values = [DataSanitizer.sanitize(v) for v in value]
                conditions.append(f"{field} IN ({', '.join(sanitized_values)})")
            else:
                sanitized_value = DataSanitizer.sanitize(value)
                conditions.append(f"{field} = '{sanitized_value}'")

        return " AND ".join(conditions) if conditions else "1=1"

    def build_sort_clause(self, sort: Dict[str, str]) -> str:
        """
        Build the sort clause based on user preferences.
        Args:
            sort (dict): Sorting parameters (field and direction).
        Returns:
            str: SQL ORDER BY clause or equivalent.
        """
        sort_clauses = [f"{field} {direction.upper()}" for field, direction in sort.items()]
        return f"ORDER BY {', '.join(sort_clauses)}" if sort_clauses else ""

    def build_pagination_clause(self, pagination: Dict[str, int]) -> str:
        """
        Build the pagination clause.
        Args:
            pagination (dict): Pagination parameters (offset and limit).
        Returns:
            str: SQL LIMIT clause or equivalent.
        """
        offset = pagination.get("offset", 0)
        limit = pagination.get("limit", 10)
        return f"LIMIT {offset}, {limit}"

    def query_database(
        self, dataset: str, conditions: str, order_clause: str, limit_clause: str
    ) -> (List[Dict[str, Any]], int):
        """
        Query the database with the constructed clauses.
        Args:
            dataset (str): The dataset to query.
            conditions (str): WHERE clause.
            order_clause (str): ORDER BY clause.
            limit_clause (str): LIMIT clause.
        Returns:
            tuple: A list of results and the total count.
        """
        try:
            query = f"""
                SELECT * FROM {dataset} WHERE {conditions} {order_clause} {limit_clause};
            """
            results = self.db.execute_query(query)

            count_query = f"SELECT COUNT(*) AS total_count FROM {dataset} WHERE {conditions};"
            total_count = self.db.execute_query(count_query)[0]["total_count"]

            return results, total_count
        except Exception as e:
            raise SearchError(f"Database query failed: {e}")

    def advanced_filtering(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform advanced filtering on the results using in-memory filtering for dynamic scenarios.
        Args:
            data (list): Data to filter.
            filters (dict): Additional filters to apply.
        Returns:
            list: Filtered data.
        """
        for field, pattern in filters.items():
            data = [
                item
                for item in data
                if field in item and re.search(pattern, str(item[field]), re.IGNORECASE)
            ]
        return data


# Example Usage
if __name__ == "__main__":
    try:
        db_conn = DatabaseConnection()
        search_service = AdvancedSearch(db_conn)

        query_params = {
            "keywords": "analytics",
            "filters": {"platform": ["YouTube", "TikTok"], "status": "active"},
            "sort": {"created_at": "desc"},
            "pagination": {"offset": 0, "limit": 20},
        }

        results = search_service.perform_search(query_params, "content_data")
        print("Search Results:", results)

    except SearchError as e:
        print(f"Search Error: {e}")
    except Exception as ex:
        print(f"Unexpected Error: {ex}")
