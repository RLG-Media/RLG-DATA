import pytest
from app import app, db
from models import Campaign, User, Platform, ContentData


@pytest.fixture(scope="module")
def client():
    """
    Sets up the Flask test client and initializes a test database.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def setup_user(client):
    """
    Sets up a default user for testing.
    """
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        return user


def login_user(client, email, password):
    """
    Helper function to log in a user and retrieve the access token.
    """
    response = client.post("/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json["access_token"]


def test_registration(client):
    """
    Test the user registration process.
    """
    response = client.post(
        "/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepassword",
        },
    )
    assert response.status_code == 201
    assert response.json["message"] == "User registered successfully"


def test_login_success(client, setup_user):
    """
    Test successful login for a registered user.
    """
    token = login_user(client, "test@example.com", "password")
    assert token is not None


def test_login_failure(client):
    """
    Test login failure for invalid credentials.
    """
    response = client.post(
        "/login", json={"email": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json["message"] == "Invalid credentials"


def test_profile_access(client, setup_user):
    """
    Test accessing the user profile with a valid JWT.
    """
    token = login_user(client, "test@example.com", "password")
    response = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json["email"] == "test@example.com"
    assert response.json["username"] == "testuser"


def test_add_platform(client, setup_user):
    """
    Test adding a platform for the user.
    """
    token = login_user(client, "test@example.com", "password")
    response = client.post(
        "/platforms",
        json={"name": "Test Platform", "api_key": "123456789"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json["message"] == "Platform added successfully"


def test_get_platforms(client, setup_user):
    """
    Test retrieving platforms for a user.
    """
    token = login_user(client, "test@example.com", "password")

    # Add a platform
    client.post(
        "/platforms",
        json={"name": "Test Platform", "api_key": "123456789"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Retrieve platforms
    response = client.get("/platforms", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Test Platform"


def test_content_data_retrieval(client, setup_user):
    """
    Test retrieving content data for a platform.
    """
    with app.app_context():
        user = setup_user
        platform = Platform(name="Test Platform", creator_id=user.id)
        db.session.add(platform)
        db.session.commit()

        content = ContentData(
            platform_id=platform.id,
            content_type="short-form",
            engagement_score=85.5,
            monetization_score=92.3,
            views=1000,
            likes=500,
            comments=100,
            shares=50,
        )
        db.session.add(content)
        db.session.commit()

    token = login_user(client, "test@example.com", "password")
    response = client.get(
        f"/content-data/{platform.id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["content_type"] == "short-form"
    assert response.json[0]["views"] == 1000


def test_campaign_creation(client, setup_user):
    """
    Test creating a campaign for the user.
    """
    token = login_user(client, "test@example.com", "password")
    response = client.post(
        "/campaigns",
        json={
            "title": "Test Campaign",
            "description": "A sample campaign for testing.",
            "start_date": "2024-11-01T00:00:00",
            "end_date": "2024-11-30T23:59:59",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json["message"] == "Campaign created successfully"


def test_campaign_retrieval(client, setup_user):
    """
    Test retrieving campaigns for the user.
    """
    with app.app_context():
        user = setup_user
        campaign = Campaign(
            user_id=user.id,
            title="Test Campaign",
            description="A sample campaign.",
            start_date="2024-11-01T00:00:00",
            end_date="2024-11-30T23:59:59",
            total_engagement=1000,
            total_revenue=500.0,
        )
        db.session.add(campaign)
        db.session.commit()

    token = login_user(client, "test@example.com", "password")
    response = client.get("/campaigns", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "Test Campaign"
