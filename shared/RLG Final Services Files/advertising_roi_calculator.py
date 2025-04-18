import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("advertising_roi.log")]
)

class AdvertisingROICalculator:
    """
    A tool to calculate Return on Investment (ROI) for advertising campaigns
    across multiple platforms including Facebook, Google, TikTok, Instagram,
    Twitter, LinkedIn, YouTube, Snapchat, Pinterest, and more.
    """

    def __init__(self, ad_data: Optional[List[Dict]] = None):
        """
        Initializes the ROI Calculator with optional preloaded ad campaign data.
        :param ad_data: A list of dictionaries containing ad campaign metrics.
        """
        self.ad_data = ad_data or []
        logging.info("Advertising ROI Calculator initialized.")

    def add_campaign_data(self, campaign: Dict):
        """
        Adds a new ad campaign's performance data.
        :param campaign: A dictionary with campaign details (platform, cost, revenue, etc.)
        """
        required_keys = {"platform", "cost", "clicks", "conversions", "revenue"}
        if not required_keys.issubset(campaign.keys()):
            logging.error("Missing required keys in campaign data: %s", campaign)
            raise ValueError("Missing required keys in campaign data.")

        self.ad_data.append(campaign)
        logging.info("Added campaign data for platform: %s", campaign["platform"])

    def calculate_roi(self, campaign: Dict) -> float:
        """
        Calculates ROI for a single campaign.
        ROI Formula: (Revenue - Cost) / Cost * 100
        :param campaign: Dictionary containing campaign details.
        :return: ROI percentage.
        """
        try:
            cost = campaign["cost"]
            revenue = campaign["revenue"]
            if cost == 0:
                return 0.0
            roi = ((revenue - cost) / cost) * 100
            return round(roi, 2)
        except Exception as e:
            logging.error("Error calculating ROI: %s", e)
            return 0.0

    def calculate_cpc(self, campaign: Dict) -> float:
        """
        Calculates Cost Per Click (CPC) for a campaign.
        CPC Formula: Cost / Clicks
        """
        try:
            cost = campaign["cost"]
            clicks = campaign["clicks"]
            if clicks == 0:
                return 0.0
            return round(cost / clicks, 2)
        except Exception as e:
            logging.error("Error calculating CPC: %s", e)
            return 0.0

    def calculate_cpa(self, campaign: Dict) -> float:
        """
        Calculates Cost Per Acquisition (CPA) for a campaign.
        CPA Formula: Cost / Conversions
        """
        try:
            cost = campaign["cost"]
            conversions = campaign["conversions"]
            if conversions == 0:
                return 0.0
            return round(cost / conversions, 2)
        except Exception as e:
            logging.error("Error calculating CPA: %s", e)
            return 0.0

    def generate_campaign_report(self) -> List[Dict]:
        """
        Generates a detailed performance report for all campaigns.
        """
        report = []
        for campaign in self.ad_data:
            campaign_report = {
                "platform": campaign["platform"],
                "roi": self.calculate_roi(campaign),
                "cpc": self.calculate_cpc(campaign),
                "cpa": self.calculate_cpa(campaign),
                "revenue": campaign["revenue"],
                "cost": campaign["cost"],
            }
            report.append(campaign_report)
        return report

if __name__ == "__main__":
    sample_data = [
        {"platform": "Facebook", "cost": 500, "clicks": 1000, "conversions": 50, "revenue": 2000},
        {"platform": "Google", "cost": 750, "clicks": 1500, "conversions": 75, "revenue": 3000},
        {"platform": "TikTok", "cost": 400, "clicks": 900, "conversions": 30, "revenue": 1800},
    ]

    roi_calculator = AdvertisingROICalculator(sample_data)
    report = roi_calculator.generate_campaign_report()

    for entry in report:
        logging.info("Platform: %s | ROI: %s%% | CPC: $%s | CPA: $%s | Revenue: $%s | Cost: $%s",
                     entry["platform"], entry["roi"], entry["cpc"], entry["cpa"], entry["revenue"], entry["cost"])
