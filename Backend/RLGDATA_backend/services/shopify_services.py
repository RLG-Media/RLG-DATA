import requests
import logging


class ShopifyService:
    """
    Service class for interacting with the Shopify API.
    """
    BASE_URL_TEMPLATE = 'https://{shop_name}.myshopify.com/admin/api/2023-01/'  # API base URL template

    def __init__(self, shop_name, access_token):
        """
        Initialize the ShopifyService with store details and API credentials.

        :param shop_name: The Shopify store name (e.g., 'your-shop-name').
        :param access_token: API access token for authentication.
        """
        self.base_url = self.BASE_URL_TEMPLATE.format(shop_name=shop_name)
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        })

    def get_products(self, limit=50, page_info=None):
        """
        Fetch products from the Shopify store with optional pagination.

        :param limit: Number of products to fetch per page (default: 50).
        :param page_info: Pagination token for fetching the next page.
        :return: A tuple containing the list of products and pagination info, or None if an error occurs.
        """
        try:
            url = f"{self.base_url}products.json"
            params = {'limit': limit}
            if page_info:
                params['page_info'] = page_info

            response = self.session.get(url, params=params)
            response.raise_for_status()

            products = response.json().get('products', [])
            pagination_info = response.links.get('next', {}).get('url', None)
            logging.info(f"Fetched {len(products)} products from Shopify.")
            return products, pagination_info

        except requests.RequestException as e:
            logging.error(f"Failed to fetch products from Shopify: {e}")
            return None, None

    def create_product(self, product_data):
        """
        Create a new product in the Shopify store.

        :param product_data: Dictionary containing product details.
        :return: Created product details or None if an error occurs.
        """
        try:
            url = f"{self.base_url}products.json"
            response = self.session.post(url, json={'product': product_data})
            response.raise_for_status()

            product = response.json().get('product', {})
            logging.info(f"Successfully created product: {product.get('title', 'Unnamed Product')}")
            return product

        except requests.RequestException as e:
            logging.error(f"Failed to create product on Shopify: {e}")
            return None

    def update_product(self, product_id, updated_data):
        """
        Update an existing product in the Shopify store.

        :param product_id: The ID of the product to update.
        :param updated_data: Dictionary containing updated product details.
        :return: Updated product details or None if an error occurs.
        """
        try:
            url = f"{self.base_url}products/{product_id}.json"
            response = self.session.put(url, json={'product': updated_data})
            response.raise_for_status()

            product = response.json().get('product', {})
            logging.info(f"Successfully updated product ID {product_id}: {product.get('title', 'Unnamed Product')}")
            return product

        except requests.RequestException as e:
            logging.error(f"Failed to update product ID {product_id} on Shopify: {e}")
            return None

    def delete_product(self, product_id):
        """
        Delete a product from the Shopify store.

        :param product_id: The ID of the product to delete.
        :return: True if the product was deleted successfully, False otherwise.
        """
        try:
            url = f"{self.base_url}products/{product_id}.json"
            response = self.session.delete(url)
            response.raise_for_status()

            logging.info(f"Successfully deleted product ID {product_id} from Shopify.")
            return True

        except requests.RequestException as e:
            logging.error(f"Failed to delete product ID {product_id} from Shopify: {e}")
            return False

    def get_orders(self, limit=50, status="any"):
        """
        Fetch orders from the Shopify store.

        :param limit: Number of orders to fetch per page (default: 50).
        :param status: Filter orders by status ('any', 'open', 'closed', 'cancelled').
        :return: List of orders or None if an error occurs.
        """
        try:
            url = f"{self.base_url}orders.json"
            params = {'limit': limit, 'status': status}
            response = self.session.get(url, params=params)
            response.raise_for_status()

            orders = response.json().get('orders', [])
            logging.info(f"Fetched {len(orders)} orders from Shopify.")
            return orders

        except requests.RequestException as e:
            logging.error(f"Failed to fetch orders from Shopify: {e}")
            return None

shopify_service = ShopifyService(
    shop_name="your-shop-name",
    access_token="your-access-token"
)
products, next_page = shopify_service.get_products(limit=20)
for product in products:
    print(product["title"])

new_product = {
    "title": "Test Product",
    "body_html": "This is a test product.",
    "vendor": "Test Vendor",
    "product_type": "Test Type",
    "variants": [{"price": "19.99"}]
}

created_product = shopify_service.create_product(new_product)
print(created_product)

updated_data = {"title": "Updated Product Title"}
updated_product = shopify_service.update_product(product_id="123456789", updated_data=updated_data)
print(updated_product)

success = shopify_service.delete_product(product_id="123456789")
print("Deleted" if success else "Failed to delete")

orders = shopify_service.get_orders(limit=10, status="open")
for order in orders:
    print(order["id"], order["email"])
