import requests
import logging

class InstagramService:
    def __init__(self, access_token):
        """
        Initialize the Instagram service with an access token.
        
        :param access_token: Access token for the Instagram API
        """
        self.access_token = access_token
        self.base_url = "https://graph.instagram.com"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

    def get_profile(self, profile_id):
        """
        Fetch profile details for a specific Instagram account.
        
        :param profile_id: The Instagram Profile ID
        :return: Profile data or None in case of failure
        """
        try:
            url = f"{self.base_url}/{profile_id}"
            params = {
                'fields': 'id,username,media_count,followers_count,follows_count',
                'access_token': self.access_token
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching Instagram profile: {e}")
            return None

    def get_profile_media(self, profile_id):
        """
        Fetch media (photos, videos) posted by a specific Instagram account.
        
        :param profile_id: The Instagram Profile ID
        :return: Media data or None in case of failure
        """
        try:
            url = f"{self.base_url}/{profile_id}/media"
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,timestamp',
                'access_token': self.access_token
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching Instagram media: {e}")
            return None

# Initialize the Instagram service with an access token
instagram_service = InstagramService(access_token='your_access_token_here')

# Fetch Instagram profile details
profile_id = 'your_instagram_profile_id_here'
profile_data = instagram_service.get_profile(profile_id)

if profile_data:
    print("Instagram Profile:", profile_data)
else:
    print("Failed to fetch Instagram profile.")

# Fetch media from an Instagram profile
media_data = instagram_service.get_profile_media(profile_id)

if media_data:
    print("Instagram Media:", media_data)
else:
    print("Failed to fetch Instagram media.")

# Initialize the Instagram service with an access token
instagram_service = InstagramService(access_token='your_access_token_here')

# Fetch Instagram profile details
profile_id = 'your_instagram_profile_id_here'
profile_data = instagram_service.get_profile(profile_id)

if profile_data:
    print("Instagram Profile:", profile_data)
else:
    print("Failed to fetch Instagram profile.")

# Fetch media from an Instagram profile
media_data = instagram_service.get_profile_media(profile_id)

if media_data:
    print("Instagram Media:", media_data)
else:
    print("Failed to fetch Instagram media.")
