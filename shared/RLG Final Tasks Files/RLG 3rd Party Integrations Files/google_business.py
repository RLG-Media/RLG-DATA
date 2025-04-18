import requests
import logging
from typing import Dict, List, Any

class GoogleBusinessManager:
    """
    A tool to manage and optimize Google Business Profiles for RLG Data and RLG Fans clients.
    Provides functionalities for fetching business information, updating profiles, and analyzing reviews.
    """

    def __init__(self, api_key: str):
        """
        Initialize the GoogleBusinessManager with the API key.
        """
        self.api_key = api_key
        self.base_url = "https://mybusiness.googleapis.com/v4"

        # Set up logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def get_locations(self) -> List[Dict[str, Any]]:
        """
        Retrieve the list of locations associated with the Google Business account.
        """
        url = f"{self.base_url}/accounts"
        params = {"key": self.api_key}

        response = requests.get(url, params=params)
        if response.status_code == 200:
            accounts = response.json().get("accounts", [])
            locations = []
            for account in accounts:
                account_id = account.get("name", "").split("/")[-1]
                locations_url = f"{self.base_url}/accounts/{account_id}/locations"
                locations_response = requests.get(locations_url, params=params)
                if locations_response.status_code == 200:
                    locations.extend(locations_response.json().get("locations", []))
                else:
                    logging.error(f"Failed to fetch locations for account {account_id}: {locations_response.text}")
            return locations
        else:
            logging.error(f"Failed to fetch accounts: {response.text}")
            return []

    def update_location_details(self, location_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update details for a specific location.
        """
        url = f"{self.base_url}/accounts/{location_id}/locations"
        params = {"key": self.api_key}
        response = requests.patch(url, json=updates, params=params)
        
        if response.status_code == 200:
            logging.info(f"Location {location_id} updated successfully.")
            return response.json()
        else:
            logging.error(f"Failed to update location {location_id}: {response.text}")
            return {"error": response.text}

    def fetch_reviews(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Fetch reviews for a specific location.
        """
        url = f"{self.base_url}/accounts/{location_id}/locations/reviews"
        params = {"key": self.api_key}

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("reviews", [])
        else:
            logging.error(f"Failed to fetch reviews for location {location_id}: {response.text}")
            return []

    def analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze customer reviews for sentiment and recurring themes.
        """
        positive, negative, neutral = 0, 0, 0
        keywords = {}

        for review in reviews:
            comment = review.get("comment", "").lower()
            rating = review.get("starRating", "")

            if rating in ["POSITIVE", "FIVE_STAR"]:
                positive += 1
            elif rating in ["NEGATIVE", "ONE_STAR"]:
                negative += 1
            else:
                neutral += 1

            for word in comment.split():
                keywords[word] = keywords.get(word, 0) + 1

        return {
            "total_reviews": len(reviews),
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "top_keywords": sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        }

    def generate_report(self, location_id: str) -> Dict[str, Any]:
        """
        Generate a detailed report for a Google Business Profile location.
        """
        reviews = self.fetch_reviews(location_id)
        analysis = self.analyze_reviews(reviews)
        location_details = self.get_location_details(location_id)

        return {
            "location_details": location_details,
            "review_analysis": analysis,
            "total_reviews": analysis.get("total_reviews"),
        }

    def get_location_details(self, location_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information about a specific location.
        """
        url = f"{self.base_url}/accounts/{location_id}/locations"
        params = {"key": self.api_key}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch details for location {location_id}: {response.text}")
            return {"error": response.text}


if __name__ == "__main__":
    # Replace with a valid API key
    api_key = "YOUR_GOOGLE_BUSINESS_API_KEY"

    google_business = GoogleBusinessManager(api_key=api_key)
    print("Fetching all business locations...")
    locations = google_business.get_locations()

    if locations:
        print(f"Found {len(locations)} locations. Generating reports...")
        for location in locations:
            location_id = location.get("name", "").split("/")[-1]
            report = google_business.generate_report(location_id)
            print(f"Report for location {location_id}:")
            print(report)
