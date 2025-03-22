import requests
from flask import current_app
from shared.utils import log_error, log_info, validate_api_response  # Shared utilities
from shared.config import DISCORD_API_BASE_URL, DISCORD_BOT_TOKEN  # Shared configurations

class DiscordService:
    """
    Service class for interacting with the Discord API, supporting message sending, guild management, and more.
    """

    def __init__(self):
        self.bot_token = DISCORD_BOT_TOKEN  # Bot token from shared config
        self.base_url = DISCORD_API_BASE_URL  # Base URL from shared config

    def send_message(self, channel_id, content, embed=None):
        """
        Send a message to a Discord channel.

        :param channel_id: The ID of the Discord channel.
        :param content: The message content (plain text).
        :param embed: (Optional) Embed content for richer message formatting.
        :return: JSON response from the Discord API or an error message.
        """
        url = f"{self.base_url}/channels/{channel_id}/messages"
        headers = self._get_headers()
        data = {'content': content}
        if embed:
            data['embed'] = embed

        try:
            response = requests.post(url, headers=headers, json=data)
            if validate_api_response(response):
                log_info(f"Message sent successfully to channel {channel_id}")
                return response.json()
            else:
                log_error(f"Failed to send message: {response.text}")
                return {'error': 'Failed to send message'}
        except requests.RequestException as e:
            log_error(f"Error sending message: {e}")
            return {'error': 'Service temporarily unavailable'}

    def get_guild_members(self, guild_id, limit=1000):
        """
        Fetch members of a Discord guild.

        :param guild_id: The ID of the guild.
        :param limit: The maximum number of members to fetch (default is 1000).
        :return: List of guild members or an error message.
        """
        url = f"{self.base_url}/guilds/{guild_id}/members"
        headers = self._get_headers()
        params = {'limit': limit}

        try:
            response = requests.get(url, headers=headers, params=params)
            if validate_api_response(response):
                log_info(f"Successfully fetched members for guild {guild_id}")
                return response.json()
            else:
                log_error(f"Failed to fetch guild members: {response.text}")
                return {'error': 'Failed to fetch guild members'}
        except requests.RequestException as e:
            log_error(f"Error fetching guild members: {e}")
            return {'error': 'Service temporarily unavailable'}

    def create_guild_role(self, guild_id, role_name, permissions=0, color=0):
        """
        Create a new role in a Discord guild.

        :param guild_id: The ID of the guild.
        :param role_name: The name of the new role.
        :param permissions: The permissions for the role (default is 0 for no permissions).
        :param color: The color of the role (default is 0 for no specific color).
        :return: JSON response from the Discord API or an error message.
        """
        url = f"{self.base_url}/guilds/{guild_id}/roles"
        headers = self._get_headers()
        data = {
            'name': role_name,
            'permissions': permissions,
            'color': color
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if validate_api_response(response):
                log_info(f"Successfully created role '{role_name}' in guild {guild_id}")
                return response.json()
            else:
                log_error(f"Failed to create role: {response.text}")
                return {'error': 'Failed to create role'}
        except requests.RequestException as e:
            log_error(f"Error creating role: {e}")
            return {'error': 'Service temporarily unavailable'}

    def _get_headers(self):
        """
        Generate headers for Discord API requests.

        :return: A dictionary containing headers.
        """
        return {
            'Authorization': f'Bot {self.bot_token}',
            'Content-Type': 'application/json'
        }

discord_service = DiscordService()
response = discord_service.send_message(channel_id="123456789", content="Hello, Discord!")
print(response)

embed = {
    "title": "Announcement",
    "description": "New feature released!",
    "color": 65280  # Green color
}
response = discord_service.send_message(channel_id="123456789", content="", embed=embed)
print(response)

members = discord_service.get_guild_members(guild_id="987654321", limit=500)
print(members)

role = discord_service.create_guild_role(guild_id="987654321", role_name="Moderator", permissions=8, color=3447003)
print(role)
