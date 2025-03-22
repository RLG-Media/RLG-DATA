import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class UITests(unittest.TestCase):
    """
    UI test suite for validating the web application's user interface and functionality.
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the Selenium WebDriver before all tests.
        """
        cls.driver = webdriver.Chrome()  # Use the appropriate WebDriver (e.g., Chrome, Firefox)
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://localhost:8000"  # Update with the correct URL of your app
        logging.info("WebDriver initialized and base URL set.")

    @classmethod
    def tearDownClass(cls):
        """
        Quit the WebDriver after all tests are complete.
        """
        cls.driver.quit()
        logging.info("WebDriver closed.")

    def test_login_page_ui(self):
        """
        Test the login page UI components and functionality.
        """
        driver = self.driver
        driver.get(f"{self.base_url}/login")

        try:
            # Check if the login form elements are present
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.ID, "login-btn")

            self.assertTrue(username_field.is_displayed(), "Username field not visible.")
            self.assertTrue(password_field.is_displayed(), "Password field not visible.")
            self.assertTrue(login_button.is_displayed(), "Login button not visible.")

            # Simulate user input and login attempt
            username_field.send_keys("testuser")
            password_field.send_keys("password123")
            login_button.click()

            # Verify successful login by checking redirection or UI changes
            WebDriverWait(driver, 10).until(
                EC.url_contains("/dashboard")
            )
            logging.info("Login page UI test passed.")
        except Exception as e:
            self.fail(f"Login page UI test failed: {e}")

    def test_dashboard_navigation(self):
        """
        Test the dashboard navigation menu and links.
        """
        driver = self.driver
        driver.get(f"{self.base_url}/dashboard")

        try:
            # Check for the presence of navigation links
            nav_links = driver.find_elements(By.CLASS_NAME, "nav-link")
            self.assertGreater(len(nav_links), 0, "No navigation links found.")

            # Test navigation by clicking on each link
            for link in nav_links:
                ActionChains(driver).move_to_element(link).click().perform()
                logging.info(f"Clicked on navigation link: {link.text}")

                # Verify page load or content change
                self.assertTrue(
                    driver.current_url.endswith(link.get_attribute("href")),
                    f"Navigation to {link.text} failed.",
                )
            logging.info("Dashboard navigation test passed.")
        except Exception as e:
            self.fail(f"Dashboard navigation test failed: {e}")

    def test_form_submission(self):
        """
        Test a sample form submission and validation.
        """
        driver = self.driver
        driver.get(f"{self.base_url}/form-page")

        try:
            # Locate form elements
            text_field = driver.find_element(By.ID, "text-input")
            dropdown = driver.find_element(By.ID, "dropdown")
            submit_button = driver.find_element(By.ID, "submit-btn")

            # Fill out the form
            text_field.send_keys("Sample input text")
            dropdown.send_keys("Option 1")
            submit_button.click()

            # Check for success message
            success_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "success-msg"))
            )
            self.assertTrue(
                success_message.is_displayed(), "Success message not displayed."
            )
            logging.info("Form submission test passed.")
        except Exception as e:
            self.fail(f"Form submission test failed: {e}")

    def test_responsive_ui(self):
        """
        Test the responsiveness of the UI at different screen resolutions.
        """
        driver = self.driver

        resolutions = [
            (1920, 1080),  # Desktop
            (1366, 768),   # Laptop
            (768, 1024),   # Tablet
            (375, 667),    # Mobile
        ]

        try:
            for width, height in resolutions:
                driver.set_window_size(width, height)
                driver.get(f"{self.base_url}/dashboard")
                logging.info(f"Testing UI responsiveness at resolution {width}x{height}.")

                # Check for specific elements to ensure layout adjusts correctly
                header = driver.find_element(By.ID, "header")
                self.assertTrue(header.is_displayed(), "Header not visible.")
                logging.info(f"UI responsive test passed for resolution {width}x{height}.")
        except Exception as e:
            self.fail(f"Responsive UI test failed: {e}")

    def test_error_pages(self):
        """
        Test the error pages (404, 500) for correct rendering.
        """
        driver = self.driver

        try:
            # Test 404 page
            driver.get(f"{self.base_url}/nonexistent-page")
            error_404 = driver.find_element(By.ID, "error-404")
            self.assertTrue(error_404.is_displayed(), "404 error page not displayed.")

            # Test 500 page (simulate by accessing a broken endpoint)
            driver.get(f"{self.base_url}/simulate-500-error")
            error_500 = driver.find_element(By.ID, "error-500")
            self.assertTrue(error_500.is_displayed(), "500 error page not displayed.")
            logging.info("Error pages test passed.")
        except Exception as e:
            self.fail(f"Error pages test failed: {e}")


if __name__ == "__main__":
    unittest.main()
