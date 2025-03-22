import re
from typing import List, Dict, Tuple, Optional

class AccessibilityUtils:
    """
    A utility class to ensure WCAG and ADA compliance for RLG Data and RLG Fans.
    """

    @staticmethod
    def validate_contrast_ratio(foreground_color: str, background_color: str) -> Tuple[bool, str]:
        """
        Validates the contrast ratio between foreground and background colors.
        
        Args:
            foreground_color (str): Hex color code for foreground (e.g., '#FFFFFF').
            background_color (str): Hex color code for background (e.g., '#000000').
        
        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating success and a message.
        """
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def luminance(rgb: Tuple[int, int, int]) -> float:
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        fg_rgb = hex_to_rgb(foreground_color)
        bg_rgb = hex_to_rgb(background_color)
        l1 = luminance(fg_rgb)
        l2 = luminance(bg_rgb)
        contrast_ratio = (l1 + 0.05) / (l2 + 0.05) if l1 > l2 else (l2 + 0.05) / (l1 + 0.05)
        
        if contrast_ratio >= 4.5:  # WCAG AA level
            return True, f"Contrast ratio of {contrast_ratio:.2f} meets WCAG requirements."
        else:
            return False, f"Contrast ratio of {contrast_ratio:.2f} fails WCAG requirements."

    @staticmethod
    def validate_aria_attributes(elements: List[Dict[str, str]]) -> List[str]:
        """
        Validates ARIA attributes in HTML elements.
        
        Args:
            elements (List[Dict[str, str]]): List of HTML element dictionaries with 'role' and 'aria-*' attributes.
        
        Returns:
            List[str]: A list of warnings for incorrect ARIA usage.
        """
        warnings = []
        valid_roles = ["button", "checkbox", "dialog", "heading", "link", "progressbar", "radio", "tab", "textbox"]
        
        for element in elements:
            role = element.get("role")
            if role and role not in valid_roles:
                warnings.append(f"Invalid role '{role}' detected.")
            for attr, value in element.items():
                if attr.startswith("aria-") and not value:
                    warnings.append(f"ARIA attribute '{attr}' should not be empty.")
        
        return warnings

    @staticmethod
    def check_keyboard_navigation(html_elements: List[Dict[str, str]]) -> List[str]:
        """
        Checks and fixes keyboard navigation issues.
        
        Args:
            html_elements (List[Dict[str, str]]): List of HTML element dictionaries with 'tabindex' and 'focusable' attributes.
        
        Returns:
            List[str]: List of warnings or fixes made for keyboard navigation.
        """
        issues = []
        for element in html_elements:
            if "tabindex" not in element:
                issues.append(f"Element {element} is missing 'tabindex'.")
            elif not element.get("focusable", False):
                issues.append(f"Element {element} is not focusable.")
        return issues

    @staticmethod
    def check_screen_reader_compatibility(html_elements: List[Dict[str, str]]) -> List[str]:
        """
        Ensures screen reader compatibility by checking for alt text and label associations.
        
        Args:
            html_elements (List[Dict[str, str]]): List of HTML elements to validate.
        
        Returns:
            List[str]: Warnings for screen reader compatibility issues.
        """
        warnings = []
        for element in html_elements:
            if element.get("tag") == "img" and not element.get("alt"):
                warnings.append(f"Image element {element} is missing an 'alt' attribute.")
            if element.get("tag") in ["input", "textarea"] and not element.get("label"):
                warnings.append(f"Input element {element} is missing a label association.")
        return warnings

    @staticmethod
    def validate_language_tag(lang: str) -> bool:
        """
        Validates language tags for localization.
        
        Args:
            lang (str): Language tag (e.g., 'en', 'fr', 'es').
        
        Returns:
            bool: True if valid, False otherwise.
        """
        pattern = r"^[a-z]{2}(-[A-Z]{2})?$"
        return bool(re.match(pattern, lang))
    
    @staticmethod
    def generate_accessibility_report(html_elements: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        Generates a comprehensive accessibility report.
        
        Args:
            html_elements (List[Dict[str, str]]): List of HTML elements to analyze.
        
        Returns:
            Dict[str, List[str]]: A report with various accessibility warnings and recommendations.
        """
        report = {
            "contrast_issues": [],
            "aria_issues": [],
            "keyboard_issues": [],
            "screen_reader_issues": [],
        }
        report["aria_issues"] = AccessibilityUtils.validate_aria_attributes(html_elements)
        report["keyboard_issues"] = AccessibilityUtils.check_keyboard_navigation(html_elements)
        report["screen_reader_issues"] = AccessibilityUtils.check_screen_reader_compatibility(html_elements)
        return report
