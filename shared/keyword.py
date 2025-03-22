import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from typing import List, Dict, Any

class KeywordResearchTool:
    def __init__(self):
        self.api_endpoints = {
            "google_trends": "https://trends.google.com/trends/api/explore",
            "search_volume": "https://api.keywordtool.io/v2/search/volume",
            "keyword_suggestions": "https://api.keywordtool.io/v2/suggestions",
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_search_volume(self, keyword: str) -> Dict[str, Any]:
        # Placeholder for search volume API
        # You may need an API like keywordtool.io, Moz, or SEMrush for detailed data
        response = requests.get(
            f"{self.api_endpoints['search_volume']}?keyword={keyword}", headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to retrieve search volume."}

    def get_keyword_suggestions(self, keyword: str) -> List[str]:
        # Placeholder for keyword suggestion API
        response = requests.get(
            f"{self.api_endpoints['keyword_suggestions']}?keyword={keyword}", headers=self.headers
        )
        if response.status_code == 200:
            suggestions = response.json().get("data", {}).get("suggestions", [])
            return [suggestion["keyword"] for suggestion in suggestions]
        return []

    def get_competitor_rankings(self, keyword: str) -> List[Dict[str, Any]]:
        # Simulate scraping search engine results to evaluate competitors
        url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
        response = requests.get(url, headers=self.headers)
        competitors = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='tF2Cxc')  # Google's result container class
            for result in results:
                title = result.find('h3').text if result.find('h3') else ""
                link = result.find('a')['href'] if result.find('a') else ""
                competitors.append({"title": title, "link": link})
        return competitors

    def calculate_keyword_strength(self, search_volume: int, competition: int) -> str:
        if search_volume > 10000 and competition < 50:
            return "High"
        elif search_volume > 5000:
            return "Medium"
        return "Low"

    def get_keyword_insights(self, keyword: str) -> Dict[str, Any]:
        search_volume_data = self.get_search_volume(keyword)
        suggestions = self.get_keyword_suggestions(keyword)
        competitors = self.get_competitor_rankings(keyword)

        if "error" in search_volume_data:
            return search_volume_data

        search_volume = search_volume_data.get("search_volume", 0)
        competition = search_volume_data.get("competition", 100)  # Assuming a scale of 0-100
        keyword_strength = self.calculate_keyword_strength(search_volume, competition)

        return {
            "keyword": keyword,
            "search_volume": search_volume,
            "competition": competition,
            "keyword_strength": keyword_strength,
            "suggestions": suggestions,
            "competitors": competitors,
        }

    def generate_report(self, keywords: List[str]) -> Dict[str, Any]:
        report = defaultdict(list)
        for keyword in keywords:
            insights = self.get_keyword_insights(keyword)
            report[keyword].append(insights)
        return report

if __name__ == "__main__":
    tool = KeywordResearchTool()
    keywords = ["digital marketing", "SEO tools", "content creation"]
    report = tool.generate_report(keywords)
    for keyword, insights in report.items():
        print(f"Insights for '{keyword}':")
        for insight in insights:
            print(insight)
            print("-" * 40)
