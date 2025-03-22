import requests
from flask import current_app
from typing import Dict, Any, Optional
from shared.utils import log_error, log_info  # Shared utilities for logging
from shared.config import INFLUENCER_MATCHING_API_URL, INFLUENCER_MATCHING_API_KEY  # Shared configurations

class InfluencerMatchingService:
    """
    Service class for matching influencers with brands or campaigns.
    Interacts with an external Influencer Matching API to search for influencers
    based on specified criteria and retrieve detailed influencer profiles.
    """

    def __init__(self, api_key: str = INFLUENCER_MATCHING_API_KEY) -> None:
        """
        Initialize the InfluencerMatchingService with the provided API key.
        
        Args:
            api_key (str): API key for authenticating with the Influencer Matching API.
        
        Raises:
            ValueError: If the API key is not provided.
        """
        if not api_key:
            raise ValueError("API key must be provided in the configuration.")
        self.api_key: str = api_key
        # Base URL for the Influencer Matching API; update with your actual endpoint.
        self.base_url: str = INFLUENCER_MATCHING_API_URL or "https://api.influencermatching.com/"
        log_info("InfluencerMatchingService initialized with base URL: %s", self.base_url)

    def find_influencers(self, criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find influencers based on specified criteria.
        
        Args:
            criteria (Dict[str, Any]): Dictionary containing search criteria for matching influencers.
                For example: {"category": "fashion", "followers_min": 1000, "location": "United States"}
        
        Returns:
            Optional[Dict[str, Any]]: JSON response from the API containing matched influencers,
                                      or None if an error occurs.
        """
        url = f"{self.base_url}influencers/search"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=criteria, timeout=10)
            if response.status_code == 200:
                log_info("Influencer search successful for criteria: %s", criteria)
                return response.json()
            else:
                current_app.logger.error(f"Failed to find influencers: {response.text}")
                return {"error": "Unable to find influencers"}
        except requests.RequestException as e:
            current_app.logger.error(f"An error occurred while finding influencers: {e}")
            return {"error": "Service temporarily unavailable"}

    def get_influencer_profile(self, influencer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the profile details of a specific influencer.
        
        Args:
            influencer_id (str): The unique ID of the influencer.
        
        Returns:
            Optional[Dict[str, Any]]: Influencer profile details as returned by the API,
                                      or None if an error occurs.
        """
        url = f"{self.base_url}influencers/{influencer_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                log_info("Influencer profile retrieved successfully for ID: %s", influencer_id)
                return response.json()
            else:
                current_app.logger.error(f"Failed to fetch influencer profile: {response.text}")
                return {"error": "Unable to fetch influencer profile"}
        except requests.RequestException as e:
            current_app.logger.error(f"An error occurred while fetching influencer profile: {e}")
            return {"error": "Service temporarily unavailable"}


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Initialize the InfluencerMatchingService with your API key
    influencer_service = InfluencerMatchingService(api_key="your_api_key_here")

    # Define search criteria for finding influencers
    criteria = {
        "category": "fashion",
        "followers_min": 1000,
        "location": "United States"
    }

    # Find influencers based on the criteria
    influencers = influencer_service.find_influencers(criteria)
    if influencers:
        print("Matched Influencers:", influencers)
    else:
        print("No influencers found or an error occurred.")

    # Get profile details for a specific influencer
    influencer_id = "123456"
    profile_details = influencer_service.get_influencer_profile(influencer_id)
    if profile_details:
        print("Influencer Profile:", profile_details)
    else:
        print("Failed to fetch influencer profile.")
