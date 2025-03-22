import unittest
from datetime import datetime, timedelta
from app import create_app, db
from models import User, ScheduledContent, ScrapingTask, Notification
from content_scheduling import schedule_content
from data_analysis import analyze_data
from scraping_utils import start_scraping_task
from notifications import send_content_reminder

class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize the Flask app and set up the test database
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
        
        # Create a test user
        cls.user = User(username="test_user", email="test_user@example.com")
        cls.user.set_password("password")
        db.session.add(cls.user)
        db.session.commit()
        
    @classmethod
    def tearDownClass(cls):
        # Clean up after tests
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        # Run before each test to reset notifications and tasks
        Notification.query.delete()
        ScheduledContent.query.delete()
        ScrapingTask.query.delete()
        db.session.commit()

    def test_schedule_content_and_reminder(self):
        """
        Test that scheduling content triggers a reminder notification at the correct time.
        """
        scheduled_time = datetime.now() + timedelta(minutes=2)
        content_text = "New scheduled content for integration test"

        # Schedule content
        schedule_response = schedule_content(
            user_id=self.user.id,
            content_text=content_text,
            scheduled_time=scheduled_time
        )
        self.assertEqual(schedule_response, "Content scheduled successfully")

        # Simulate sending reminder
        scheduled_content = ScheduledContent.query.filter_by(content_text=content_text).first()
        send_content_reminder(scheduled_content.id)
        
        # Verify notification
        reminder = Notification.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(reminder, "Reminder notification not sent.")
        self.assertEqual(reminder.message, f"Reminder: Scheduled content '{content_text}' is due now.")

    def test_data_scraping_and_analysis_integration(self):
        """
        Test that data scraping integrates with data analysis and produces correct insights.
        """
        url = "http://example.com"
        platform = "OnlyFans"
        
        # Start scraping task
        scraping_response = start_scraping_task(url, platform, self.user.id)
        self.assertEqual(scraping_response, "Scraping task initiated")
        
        # Simulate completion of scraping task and analysis
        scraping_task = ScrapingTask.query.filter_by(url=url).first()
        scraping_task.status = "complete"
        scraping_task.result = "Sample scraped data for analysis"
        db.session.commit()

        # Run data analysis
        analysis_results = analyze_data(scraping_task.result)
        self.assertIn("insights", analysis_results, "Analysis results should contain 'insights'.")
        
        # Ensure insights and recommendations are present
        self.assertTrue(analysis_results["insights"], "Data analysis should generate insights.")

    def test_full_integration_content_scheduling_scraping_and_notifications(self):
        """
        Full integration test covering content scheduling, scraping, analysis, and notifications.
        """
        # Schedule content
        scheduled_time = datetime.now() + timedelta(minutes=5)
        schedule_content(
            user_id=self.user.id,
            content_text="Content scheduling and scraping test",
            scheduled_time=scheduled_time
        )
        
        # Trigger scraping task
        url = "http://content-platform.com/test"
        start_scraping_task(url, "FANfix", self.user.id)
        
        # Simulate scraping completion and run analysis
        scraping_task = ScrapingTask.query.filter_by(url=url).first()
        scraping_task.status = "complete"
        scraping_task.result = "Scraped data for full integration test"
        db.session.commit()

        analysis_results = analyze_data(scraping_task.result)
        
        # Check analysis insights
        self.assertIn("insights", analysis_results, "Insights missing in analysis results.")
        
        # Simulate sending reminder
        scheduled_content = ScheduledContent.query.first()
        send_content_reminder(scheduled_content.id)
        
        # Validate notifications
        reminder = Notification.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(reminder, "Notification for scheduled content reminder was not sent.")
        self.assertIn("Reminder:", reminder.message, "Reminder message not formatted correctly.")

if __name__ == '__main__':
    unittest.main()
