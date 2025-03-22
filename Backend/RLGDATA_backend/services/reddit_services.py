import requests
import logging
from requests.auth import HTTPBasicAuth
from typing import Dict, Any, Optional, List
from flask import current_app

# Configure logging (if not already configured elsewhere)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class RedditService:
    """
    A service class to interact with the Reddit API.
    
    Supports both app-based (client credentials) and script-based (username/password) authentication.
    Provides methods to fetch user profiles, subreddit posts, post comments, search subreddits,
    and fetch user comments.
    """
    
    BASE_URL: str = "https://www.reddit.com/api/v1"
    API_URL: str = "https://oauth.reddit.com"
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str,
                 username: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Initialize the RedditService with API credentials.
        
        Args:
            client_id (str): Reddit API client ID.
            client_secret (str): Reddit API client secret.
            user_agent (str): Custom user agent for the API requests.
            username (Optional[str]): Reddit username for script-based authentication.
            password (Optional[str]): Reddit password for script-based authentication.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.username = username
        self.password = password
        self.access_token: Optional[str] = None

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        logger.info("RedditService initialized with user agent: %s", self.user_agent)

    def authenticate(self) -> bool:
        """
        Authenticate with the Reddit API to obtain an access token.
        Supports script-based authentication (if username and password are provided)
        or app-only authentication (client_credentials).
        
        Returns:
            bool: True if authentication succeeds, False otherwise.
        """
        try:
            # Choose grant type based on presence of username/password
            if self.username and self.password:
                data = {
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password
                }
            else:
                data = {"grant_type": "client_credentials"}

            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            response = self.session.post(f"{self.BASE_URL}/access_token", data=data, auth=auth, timeout=10)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get("access_token")
            if not self.access_token:
                logger.error("Authentication failed: no access token returned.")
                return False

            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            logger.info("Authenticated successfully with the Reddit API.")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to authenticate with the Reddit API: {e}")
            return False

    def fetch_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch public profile information for a Reddit user.
        
        Args:
            username (str): Reddit username.
        
        Returns:
            Optional[Dict[str, Any]]: User profile data as a dictionary or None if an error occurs.
        """
        try:
            url = f"{self.API_URL}/user/{username}/about"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            logger.info("Fetched profile data for Reddit user: %s.", username)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch user profile for {username}: {e}")
            return None

    def fetch_subreddit_posts(self, subreddit: str, limit: int = 10, sort: str = "hot") -> Optional[List[Dict[str, Any]]]:
        """
        Fetch posts from a subreddit.
        
        Args:
            subreddit (str): Name of the subreddit (e.g., 'learnpython').
            limit (int): Number of posts to fetch (default: 10).
            sort (str): Sort order ('hot', 'new', 'top', etc.).
        
        Returns:
            Optional[List[Dict[str, Any]]]: List of posts as dictionaries or None if an error occurs.
        """
        try:
            url = f"{self.API_URL}/r/{subreddit}/{sort}"
            params = {"limit": limit}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            logger.info("Fetched %d posts from subreddit: %s (%s).", limit, subreddit, sort)
            data = response.json()
            # The actual posts are under data -> children (each is a dict with key "data")
            posts = data.get("data", {}).get("children", [])
            return posts
        except requests.RequestException as e:
            logger.error(f"Failed to fetch posts from subreddit {subreddit}: {e}")
            return None

    def post_comment(self, post_id: str, comment_text: str) -> Optional[Dict[str, Any]]:
        """
        Post a comment on a specific Reddit post.
        
        Args:
            post_id (str): The ID of the Reddit post (e.g., 't3_abc123').
            comment_text (str): The content of the comment.
        
        Returns:
            Optional[Dict[str, Any]]: Response data for the posted comment or None if an error occurs.
        """
        try:
            url = f"{self.API_URL}/api/comment"
            data = {
                "thing_id": post_id,
                "text": comment_text
            }
            response = self.session.post(url, data=data, timeout=10)
            response.raise_for_status()
            logger.info("Posted comment on post %s.", post_id)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to post comment on post {post_id}: {e}")
            return None

    def search_subreddits(self, query: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Search for subreddits matching a query.
        
        Args:
            query (str): Search query string.
            limit (int): Number of results to return (default: 10).
        
        Returns:
            Optional[List[Dict[str, Any]]]: List of subreddit data as dictionaries or None if an error occurs.
        """
        try:
            url = f"{self.API_URL}/subreddits/search"
            params = {"q": query, "limit": limit}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            logger.info("Fetched subreddits matching query: %s.", query)
            data = response.json()
            return data.get("data", {}).get("children", [])
        except requests.RequestException as e:
            logger.error(f"Failed to search subreddits with query '{query}': {e}")
            return None

    def fetch_user_comments(self, username: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch recent comments made by a Reddit user.
        
        Args:
            username (str): Reddit username.
            limit (int): Number of comments to fetch (default: 10).
        
        Returns:
            Optional[List[Dict[str, Any]]]: List of comment data as dictionaries or None if an error occurs.
        """
        try:
            url = f"{self.API_URL}/user/{username}/comments"
            params = {"limit": limit}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            logger.info("Fetched recent comments for user: %s.", username)
            data = response.json()
            return data.get("data", {}).get("children", [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch comments for user {username}: {e}")
            return None

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Initialize the RedditService with your credentials.
    reddit_service = RedditService(
        client_id="your_client_id",
        client_secret="your_client_secret",
        user_agent="your_user_agent",
        username="your_username",  # Optional, for script-based authentication
        password="your_password"   # Optional, for script-based authentication
    )

    if reddit_service.authenticate():
        print("Authenticated successfully.")
    else:
        print("Authentication failed.")

    # Fetch and print a user profile.
    user_profile = reddit_service.fetch_user_profile("reddit_username")
    print("User Profile:", user_profile)

    # Fetch and print posts from a subreddit.
    posts = reddit_service.fetch_subreddit_posts("learnpython", limit=5)
    if posts:
        for post in posts:
            print("Post Title:", post.get("data", {}).get("title"))
    else:
        print("No posts retrieved.")

    # Optionally, post a comment on a specific post (uncomment to test)
    # comment_response = reddit_service.post_comment("t3_example", "This is a test comment.")
    # print("Comment Response:", comment_response)

    # Search for subreddits based on a query.
    subreddits = reddit_service.search_subreddits("Python", limit=5)
    print("Subreddits:", subreddits)

    # Fetch recent comments for a user.
    user_comments = reddit_service.fetch_user_comments("reddit_username", limit=5)
    print("User Comments:", user_comments)
