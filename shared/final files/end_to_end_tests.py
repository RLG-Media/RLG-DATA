import pytest
import json
import requests
from cryptography.hazmat.primitives import hashes
from encryption_utils import derive_key, encrypt_data, decrypt_data, generate_salt, generate_rsa_keys
from models import User, Product, Order  # Example model imports
from app import app  # Assuming Flask app is in app.py

# Test configuration
BASE_URL = "http://localhost:5000"  # Adjust this based on your environment
API_KEY = "your_api_key_here"  # Replace with your actual API key

# Setup and teardown functions
@pytest.fixture(scope="module")
def setup():
    """Setup test environment."""
    # Generate a salt and a derived key for encryption tests
    salt = generate_salt()
    password = "strongpassword123"
    key = derive_key(password, salt)

    # Create RSA keys for encryption tests
    rsa_keys = generate_rsa_keys()

    # Setup: Add user and sample data to the database
    user = User(username="testuser", email="testuser@example.com")
    product = Product(name="Test Product", price=100)
    order = Order(user_id=user.id, product_id=product.id, quantity=2)

    # Assuming DB session setup (example with SQLAlchemy)
    db.session.add(user)
    db.session.add(product)
    db.session.add(order)
    db.session.commit()

    yield {
        "salt": salt,
        "key": key,
        "user": user,
        "product": product,
        "order": order,
        "rsa_keys": rsa_keys,
    }

    # Teardown: Clean up the database after tests
    db.session.remove()
    db.drop_all()

# Test API Endpoints
def test_get_user(setup):
    """Test retrieving a user."""
    user = setup["user"]
    response = requests.get(f"{BASE_URL}/api/users/{user.id}", headers={"Authorization": f"Bearer {API_KEY}"})
    assert response.status_code == 200
    assert response.json()["id"] == user.id
    assert response.json()["email"] == user.email

def test_create_order(setup):
    """Test creating an order."""
    user = setup["user"]
    product = setup["product"]
    data = {
        "user_id": user.id,
        "product_id": product.id,
        "quantity": 1,
    }
    response = requests.post(f"{BASE_URL}/api/orders", json=data, headers={"Authorization": f"Bearer {API_KEY}"})
    assert response.status_code == 201
    assert response.json()["user_id"] == user.id
    assert response.json()["product_id"] == product.id
    assert response.json()["quantity"] == 1

def test_update_order(setup):
    """Test updating an order."""
    order = setup["order"]
    updated_data = {
        "quantity": 3,
    }
    response = requests.put(f"{BASE_URL}/api/orders/{order.id}", json=updated_data, headers={"Authorization": f"Bearer {API_KEY}"})
    assert response.status_code == 200
    assert response.json()["quantity"] == 3

def test_delete_order(setup):
    """Test deleting an order."""
    order = setup["order"]
    response = requests.delete(f"{BASE_URL}/api/orders/{order.id}", headers={"Authorization": f"Bearer {API_KEY}"})
    assert response.status_code == 204
    response_check = requests.get(f"{BASE_URL}/api/orders/{order.id}", headers={"Authorization": f"Bearer {API_KEY}"})
    assert response_check.status_code == 404  # Order should be deleted

# Test Encryption and Decryption
def test_encrypt_decrypt_data(setup):
    """Test encryption and decryption of data."""
    key = setup["key"]
    data_to_encrypt = "Sensitive user data"
    
    encrypted = encrypt_data(key, data_to_encrypt)
    decrypted = decrypt_data(key, encrypted)

    assert decrypted == data_to_encrypt  # Ensure the decrypted data matches the original

# Test RSA Encryption and Decryption
def test_rsa_encryption_decryption(setup):
    """Test RSA encryption and decryption."""
    rsa_keys = setup["rsa_keys"]
    data_to_encrypt = "Sensitive data for RSA"
    
    rsa_encrypted = encrypt_with_rsa(rsa_keys["public_key"], data_to_encrypt)
    rsa_decrypted = decrypt_with_rsa(rsa_keys["private_key"], rsa_encrypted)

    assert rsa_decrypted == data_to_encrypt  # Ensure the decrypted data matches the original

# Test Authentication and Authorization
def test_user_authentication():
    """Test user authentication."""
    credentials = {"username": "testuser", "password": "strongpassword123"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials)
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token is not None

def test_invalid_authentication():
    """Test invalid user authentication."""
    credentials = {"username": "wronguser", "password": "wrongpassword"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials)
    assert response.status_code == 401  # Unauthorized

# Test Data Integrity
def test_data_storage_integrity(setup):
    """Test data consistency after storage and retrieval."""
    user = setup["user"]
    product = setup["product"]

    # Simulate saving user data
    saved_user = db.session.query(User).filter_by(id=user.id).first()
    assert saved_user.username == user.username
    assert saved_user.email == user.email

    # Simulate saving product data
    saved_product = db.session.query(Product).filter_by(id=product.id).first()
    assert saved_product.name == product.name
    assert saved_product.price == product.price

# Test Performance
def test_api_performance():
    """Test API performance under load."""
    import time
    start_time = time.time()

    # Make multiple requests to simulate load
    for _ in range(100):  # Adjust number for load testing
        response = requests.get(f"{BASE_URL}/api/users", headers={"Authorization": f"Bearer {API_KEY}"})
        assert response.status_code == 200

    end_time = time.time()
    duration = end_time - start_time
    assert duration < 5  # Ensure the tests run within a reasonable time (5 seconds for 100 requests)

# Running the tests
if __name__ == "__main__":
    pytest.main()
