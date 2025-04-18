# scraping_config.py - Configuration for Web Scraping in RLG Data and RLG Fans

import os

class ScrapingConfig:
    """
    Configuration class for web scraping tasks.
    Handles various configurations and settings required to run web scraping effectively.
    """

    def __init__(self):
        # Base URLs for scraping from different platforms
        self.base_urls = {
            'FANfix': 'https://www.fanfix.com',
            'Fansly': 'https://www.fansly.com',
            'FanCentro': 'https://www.fancentro.com',
            'MYM.fans': 'https://www.mym.fans',
            'Fanvue': 'https://www.fanvue.com',
            'iFans': 'https://www.ifans.com',
            'FanSo': 'https://www.fanso.com',
            'FanTime': 'https://www.fantime.com',
            'Patreon': 'https://www.patreon.com',
            'Unlocked': 'https://www.unlocked.com',
            'AdultNode': 'https://www.adultnode.com',
            'Unfiltrd': 'https://www.unfiltrd.com',
            'Flirtback': 'https://www.flirtback.com',
            'AdmireMeVIP': 'https://www.admireme.vip',
            'JustForFans': 'https://www.justfor.fans',
            'ManyVids': 'https://www.manyvids.com',
            'ScrileConnect': 'https://www.scrileconnect.com',
            'OkFans': 'https://www.okfans.com',
            'Fapello': 'https://www.fapello.com',
            'Fansmetrics': 'https://www.fansmetrics.com',
            'SimpCity': 'https://www.simpcity.su',
            'AVNStars': 'https://www.avnstars.com'
        }

        # User-agent for HTTP requests (could be rotated for better scraping results)
        self.user_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # List of platforms to scrape
        self.scraping_platforms = list(self.base_urls.keys())

        # Path where scraped data should be stored
        self.data_storage_path = os.path.join(os.path.dirname(__file__), 'scraped_data')

        # Timeout settings for HTTP requests during scraping
        self.request_timeout = 30  # in seconds

        # Maximum retries for HTTP requests in case of failures
        self.max_retries = 3

        # Retry backoff factor for handling failed requests
        self.retry_backoff_factor = 1.5

        # Delay between each request to avoid overwhelming servers
        self.request_delay = 2  # in seconds

        # Proxy configuration (if needed for anonymity during scraping)
        self.proxy_settings = {
            'enabled': False,  # Enable or disable proxy use
            'http': None,       # HTTP proxy URL
            'https': None       # HTTPS proxy URL
        }

        # Path to store images, videos, and other media from the scraping process
        self.media_storage_path = os.path.join(os.path.dirname(__file__), 'scraped_media')

        # Logging configuration for scraping activities
        self.log_file_path = os.path.join(os.path.dirname(__file__), 'scraping_logs')
        self.log_level = 'DEBUG'  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL

        # Number of concurrent scraping tasks
        self.concurrent_tasks = 10

        # Headers used for authentication (if any platform requires it)
        self.auth_headers = {
            'Authorization': None  # Example: 'Bearer <your_api_key>'
        }

        # Scraping frequency for each platform (daily, weekly, etc.)
        self.scraping_frequency = {
            'FANfix': 'daily',
            'Fansly': 'daily',
            'FanCentro': 'daily',
            'MYM.fans': 'daily',
            'Fanvue': 'daily',
            'iFans': 'daily',
            'FanSo': 'daily',
            'FanTime': 'daily',
            'Patreon': 'daily',
            'Unlocked': 'daily',
            'AdultNode': 'daily',
            'Unfiltrd': 'daily',
            'Flirtback': 'daily',
            'AdmireMeVIP': 'daily',
            'JustForFans': 'daily',
            'ManyVids': 'daily',
            'ScrileConnect': 'daily',
            'OkFans': 'daily',
            'Fapello': 'daily',
            'Fansmetrics': 'daily',
            'SimpCity': 'daily',
            'AVNStars': 'daily'
        }

        # Default user agent rotation frequency
        self.user_agent_rotation_frequency = 100  # Number of requests before changing the user-agent

        # List of headers for scraping
        self.headers_list = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
            }
        ]

    def get_base_url(self, platform_name):
        """
        Get the base URL for the specified platform.
        
        Args:
            platform_name: Name of the platform (e.g., 'FANfix', 'Fansly')
        
        Returns:
            Base URL for the platform, or None if the platform is not supported.
        """
        return self.base_urls.get(platform_name)

    def get_scraping_frequency(self, platform_name):
        """
        Get the scraping frequency for the specified platform.
        
        Args:
            platform_name: Name of the platform
        
        Returns:
            Scraping frequency (daily, weekly, etc.) or None if the platform is not supported.
        """
        return self.scraping_frequency.get(platform_name)

    def get_proxy_settings(self):
        """
        Get the proxy settings for the scraper (if enabled).
        
        Returns:
            Dictionary containing HTTP and HTTPS proxy URLs, or None if proxies are not enabled.
        """
        return self.proxy_settings if self.proxy_settings['enabled'] else None

    def get_media_storage_path(self):
        """
        Get the path where scraped media (images, videos) should be stored.
        
        Returns:
            Path to media storage.
        """
        return self.media_storage_path

    def get_user_agent(self):
        """
        Get the user agent for making HTTP requests.
        
        Returns:
            User-agent string for scraping.
        """
        return self.user_agent['User-Agent']

    def get_request_timeout(self):
        """
        Get the request timeout value for HTTP requests during scraping.
        
        Returns:
            Timeout value in seconds.
        """
        return self.request_timeout

    def get_max_retries(self):
        """
        Get the maximum number of retries for HTTP requests.
        
        Returns:
            Maximum retries count.
        """
        return self.max_retries

    def get_request_delay(self):
        """
        Get the delay between each HTTP request.
        
        Returns:
            Delay in seconds.
        """
        return self.request_delay

    def get_headers_list(self):
        """
        Get the list of headers (User-Agents) used for rotating scraping requests.
        
        Returns:
            List of header dictionaries.
        """
        return self.headers_list

    def get_concurrent_tasks(self):
        """
        Get the number of concurrent scraping tasks.
        
        Returns:
            Number of concurrent tasks.
        """
        return self.concurrent_tasks

    def get_scraping_config(self):
        """
        Return a comprehensive dictionary containing all scraping configurations.
        
        Returns:
            Dictionary with all configurations.
        """
        return {
            "base_urls": self.base_urls,
            "user_agent": self.user_agent,
            "scraping_platforms": self.scraping_platforms,
            "data_storage_path": self.data_storage_path,
            "request_timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "retry_backoff_factor": self.retry_backoff_factor,
            "request_delay": self.request_delay,
            "proxy_settings": self.proxy_settings,
            "media_storage_path": self.media_storage_path,
            "log_file_path": self.log_file_path,
            "log_level": self.log_level,
            "concurrent_tasks": self.concurrent_tasks,
            "auth_headers": self.auth_headers,
            "scraping_frequency": self.scraping_frequency,
            "user_agent_rotation_frequency": self.user_agent_rotation_frequency,
            "headers_list": self.headers_list
        }
