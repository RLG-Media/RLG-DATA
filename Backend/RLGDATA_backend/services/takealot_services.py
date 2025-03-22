import requests
import logging


class TakealotService:
    """
    Service class for interacting with the Takealot API.
    """
    BASE_URL = 'https://api.takealot.com/v1/'  # Placeholder for Takealot API base URL

    def __init__(self, api_key):
        """
        Initialize the TakealotService with the provided API key.
        
        :param api_key: API key for authenticating requests.
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })

    def search_products(self, query, page=1, per_page=20):
        """
        Search for products on Takealot.
        
        :param query: The search query string.
        :param page: The page number for paginated results (default: 1).
        :param per_page: The number of results per page (default: 20).
        :return: JSON response containing product search results or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}products/search"
            params = {
                'query': query,
                'page': page,
                'per_page': per_page
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            logging.info(f"Successfully searched for products with query: {query}")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to search products on Takealot: {e}")
            return None

    def get_product_details(self, product_id):
        """
        Get details about a specific Takealot product.
        
        :param product_id: The ID of the product.
        :return: JSON response containing product details or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}products/{product_id}"
            response = self.session.get(url)
            response.raise_for_status()

            logging.info(f"Successfully fetched product details for product ID: {product_id}")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch product details from Takealot: {e}")
            return None

    def get_category_products(self, category_id, page=1, per_page=20):
        """
        Fetch products within a specific category on Takealot.
        
        :param category_id: The ID of the category.
        :param page: The page number for paginated results (default: 1).
        :param per_page: The number of results per page (default: 20).
        :return: JSON response containing category products or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}categories/{category_id}/products"
            params = {
                'page': page,
                'per_page': per_page
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched products for category ID: {category_id}")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch category products from Takealot: {e}")
            return None

    def create_product_review(self, product_id, rating, review_text):
        """
        Submit a review for a specific product on Takealot.
        
        :param product_id: The ID of the product to review.
        :param rating: The rating to give (1-5).
        :param review_text: The text of the review.
        :return: JSON response containing review confirmation or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}products/{product_id}/reviews"
            payload = {
                'rating': rating,
                'review_text': review_text
            }

            response = self.session.post(url, json=payload)
            response.raise_for_status()

            logging.info(f"Successfully submitted review for product ID: {product_id}")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to submit review for product ID {product_id}: {e}")
            return None

    def get_product_reviews(self, product_id, page=1, per_page=10):
        """
        Fetch reviews for a specific Takealot product.
        
        :param product_id: The ID of the product.
        :param page: The page number for paginated results (default: 1).
        :param per_page: The number of results per page (default: 10).
        :return: JSON response containing product reviews or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}products/{product_id}/reviews"
            params = {
                'page': page,
                'per_page': per_page
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched reviews for product ID: {product_id}")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch reviews for product ID {product_id}: {e}")
            return None

takealot_service = TakealotService(api_key="your-api-key")

products = takealot_service.search_products(query="laptop", page=1, per_page=10)
print(products)

product_details = takealot_service.get_product_details(product_id="12345")
print(product_details)

category_products = takealot_service.get_category_products(category_id="electronics", page=1)
print(category_products)

review_response = takealot_service.create_product_review(
    product_id="12345", rating=5, review_text="Excellent product!"
)
print(review_response)

reviews = takealot_service.get_product_reviews(product_id="12345", page=1)
print(reviews)
