import json
from typing import List, Dict, Optional


class DashboardSettings:
    """
    Manages dashboard configurations, including widgets, themes, and layouts.
    """

    def __init__(self, user_role: str):
        """
        Initializes the dashboard settings for a specific user role.
        :param user_role: The role of the user (e.g., "admin", "creator", "brand_manager").
        """
        self.user_role = user_role
        self.default_settings = self.load_default_settings()
        self.user_settings = self.load_user_settings()

    # --- Default Settings ---
    def load_default_settings(self) -> Dict:
        """
        Loads the default dashboard settings.
        :return: Dictionary containing default settings.
        """
        return {
            "theme": "light",
            "language": "en",
            "widgets": ["overview", "analytics", "notifications"],
            "layout": "grid",
            "refresh_interval": 60,  # Default refresh interval in seconds
        }

    # --- User Settings ---
    def load_user_settings(self) -> Dict:
        """
        Loads user-specific settings, if available.
        :return: Dictionary containing user-specific settings.
        """
        try:
            with open(f"user_settings/{self.user_role}_dashboard.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return self.default_settings

    def save_user_settings(self):
        """
        Saves the current user-specific settings to a file.
        """
        with open(f"user_settings/{self.user_role}_dashboard.json", "w") as file:
            json.dump(self.user_settings, file, indent=4)

    # --- Theme Management ---
    def set_theme(self, theme: str):
        """
        Updates the dashboard theme.
        :param theme: Theme name ("light", "dark", or custom).
        """
        if theme not in ["light", "dark"]:
            raise ValueError("Invalid theme. Choose 'light' or 'dark'.")
        self.user_settings["theme"] = theme
        self.save_user_settings()

    def get_theme(self) -> str:
        """
        Retrieves the current theme.
        :return: Current theme.
        """
        return self.user_settings.get("theme", "light")

    # --- Language Management ---
    def set_language(self, language: str):
        """
        Updates the dashboard language.
        :param language: Language code (e.g., "en", "es", "fr").
        """
        self.user_settings["language"] = language
        self.save_user_settings()

    def get_language(self) -> str:
        """
        Retrieves the current language.
        :return: Current language code.
        """
        return self.user_settings.get("language", "en")

    # --- Widget Management ---
    def add_widget(self, widget: str):
        """
        Adds a new widget to the dashboard.
        :param widget: Widget name.
        """
        if widget not in self.user_settings["widgets"]:
            self.user_settings["widgets"].append(widget)
            self.save_user_settings()

    def remove_widget(self, widget: str):
        """
        Removes a widget from the dashboard.
        :param widget: Widget name.
        """
        if widget in self.user_settings["widgets"]:
            self.user_settings["widgets"].remove(widget)
            self.save_user_settings()

    def get_widgets(self) -> List[str]:
        """
        Retrieves the list of widgets on the dashboard.
        :return: List of widget names.
        """
        return self.user_settings.get("widgets", [])

    # --- Layout Management ---
    def set_layout(self, layout: str):
        """
        Sets the dashboard layout.
        :param layout: Layout type ("grid", "list", or "custom").
        """
        if layout not in ["grid", "list"]:
            raise ValueError("Invalid layout. Choose 'grid' or 'list'.")
        self.user_settings["layout"] = layout
        self.save_user_settings()

    def get_layout(self) -> str:
        """
        Retrieves the current layout type.
        :return: Layout type.
        """
        return self.user_settings.get("layout", "grid")

    # --- Data Refresh Settings ---
    def set_refresh_interval(self, interval: int):
        """
        Sets the data refresh interval.
        :param interval: Refresh interval in seconds.
        """
        if interval < 10:
            raise ValueError("Refresh interval must be at least 10 seconds.")
        self.user_settings["refresh_interval"] = interval
        self.save_user_settings()

    def get_refresh_interval(self) -> int:
        """
        Retrieves the data refresh interval.
        :return: Refresh interval in seconds.
        """
        return self.user_settings.get("refresh_interval", 60)

    # --- Role-Based Configurations ---
    def get_role_specific_widgets(self) -> List[str]:
        """
        Returns role-specific widgets.
        :return: List of widgets tailored to the user's role.
        """
        role_widgets = {
            "admin": ["overview", "user_management", "system_status", "analytics"],
            "creator": ["overview", "analytics", "content_calendar", "monetization"],
            "brand_manager": ["overview", "brand_health", "content_performance", "campaigns"],
        }
        return role_widgets.get(self.user_role, self.default_settings["widgets"])


# Example Usage
if __name__ == "__main__":
    # Example for a content creator
    dashboard = DashboardSettings(user_role="creator")
    print("Current Theme:", dashboard.get_theme())
    dashboard.set_theme("dark")
    print("Updated Theme:", dashboard.get_theme())

    print("Current Widgets:", dashboard.get_widgets())
    dashboard.add_widget("trending_content")
    print("Widgets after addition:", dashboard.get_widgets())

    dashboard.set_refresh_interval(30)
    print("Refresh Interval:", dashboard.get_refresh_interval())
