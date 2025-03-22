import uuid
from datetime import datetime
from typing import Optional, Dict, List


class UserProfileService:
    """
    Manages user profile operations such as creation, updates, retrieval, and deletion
    for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.user_profiles = {}  # Store user profiles in {user_id: profile_data}

    def create_user_profile(
        self,
        email: str,
        first_name: str,
        last_name: str,
        subscription_type: str = "free",
        location: Optional[str] = None,
        additional_info: Optional[Dict] = None,
    ) -> str:
        """
        Create a new user profile.

        Args:
            email (str): User's email address.
            first_name (str): User's first name.
            last_name (str): User's last name.
            subscription_type (str): Type of subscription ('free', 'premium', etc.).
            location (Optional[str]): User's geographical location.
            additional_info (Optional[Dict]): Any additional user profile details.

        Returns:
            str: The ID of the created user profile.
        """
        user_id = str(uuid.uuid4())
        profile_data = {
            "user_id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "subscription_type": subscription_type,
            "location": location,
            "additional_info": additional_info or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        self.user_profiles[user_id] = profile_data

        print(f"[{datetime.now()}] Created user profile: {profile_data}")
        return user_id

    def update_user_profile(self, user_id: str, updates: Dict) -> bool:
        """
        Update an existing user profile.

        Args:
            user_id (str): ID of the user profile to update.
            updates (Dict): Dictionary of fields to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        profile = self.user_profiles.get(user_id)
        if not profile:
            print(f"[{datetime.now()}] User profile {user_id} not found.")
            return False

        profile.update({key: value for key, value in updates.items() if key in profile})
        profile["updated_at"] = datetime.now()

        print(f"[{datetime.now()}] Updated user profile {user_id}: {updates}")
        return True

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Retrieve a user profile by user ID.

        Args:
            user_id (str): ID of the user profile to retrieve.

        Returns:
            Optional[Dict]: User profile data if found, None otherwise.
        """
        profile = self.user_profiles.get(user_id)
        if not profile:
            print(f"[{datetime.now()}] User profile {user_id} not found.")
            return None

        print(f"[{datetime.now()}] Retrieved user profile: {profile}")
        return profile

    def delete_user_profile(self, user_id: str) -> bool:
        """
        Delete a user profile.

        Args:
            user_id (str): ID of the user profile to delete.

        Returns:
            bool: True if the profile was deleted, False otherwise.
        """
        if user_id not in self.user_profiles:
            print(f"[{datetime.now()}] User profile {user_id} not found.")
            return False

        del self.user_profiles[user_id]
        print(f"[{datetime.now()}] Deleted user profile {user_id}.")
        return True

    def list_user_profiles(self, subscription_type: Optional[str] = None) -> List[Dict]:
        """
        List all user profiles, optionally filtered by subscription type.

        Args:
            subscription_type (Optional[str]): Filter profiles by subscription type.

        Returns:
            List[Dict]: A list of user profiles.
        """
        profiles = list(self.user_profiles.values())
        if subscription_type:
            profiles = [profile for profile in profiles if profile["subscription_type"] == subscription_type]

        print(f"[{datetime.now()}] Listing user profiles: {len(profiles)} found.")
        return profiles

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Retrieve a user profile by email.

        Args:
            email (str): User's email address.

        Returns:
            Optional[Dict]: User profile data if found, None otherwise.
        """
        for profile in self.user_profiles.values():
            if profile["email"].lower() == email.lower():
                print(f"[{datetime.now()}] Retrieved profile by email {email}: {profile}")
                return profile

        print(f"[{datetime.now()}] No profile found for email {email}.")
        return None


# Example Usage
if __name__ == "__main__":
    profile_service = UserProfileService()

    # Create a user profile
    user_id = profile_service.create_user_profile(
        email="testuser@example.com",
        first_name="John",
        last_name="Doe",
        subscription_type="premium",
        location="USA",
    )

    # Update the profile
    profile_service.update_user_profile(user_id, {"location": "Canada", "subscription_type": "free"})

    # Retrieve the profile
    user_profile = profile_service.get_user_profile(user_id)

    # Find a profile by email
    email_search = profile_service.get_user_by_email("testuser@example.com")

    # List all profiles
    all_profiles = profile_service.list_user_profiles()

    # Delete the profile
    profile_service.delete_user_profile(user_id)
