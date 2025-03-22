import unittest
from datetime import datetime, timedelta
from content_scheduling import schedule_content, send_content_reminder
from models import db, ScheduledContent, User
from notifications import Notification

class TestContentScheduling(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize any setup required at the start of the tests
        db.create_all()  # Create tables in the test database
        cls.user = User(username="test_user", email="test_user@example.com")
        db.session.add(cls.user)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        # Clean up after all tests are done
        db.session.remove()
        db.drop_all()

    def setUp(self):
        # Set up a clean state for each test
        self.scheduled_time = datetime.now() + timedelta(minutes=5)
        self.content_data = {
            "user_id": self.user.id,
            "content_text": "New content for testing scheduling",
            "scheduled_time": self.scheduled_time
        }
        self.scheduled_content = ScheduledContent(**self.content_data)
        db.session.add(self.scheduled_content)
        db.session.commit()

    def tearDown(self):
        # Remove all scheduled content and notifications after each test
        ScheduledContent.query.delete()
        Notification.query.delete()
        db.session.commit()

    def test_schedule_content(self):
        """
        Test that content scheduling adds content to the database
        with the correct user, content, and scheduled time.
        """
        response = schedule_content(
            user_id=self.user.id,
            content_text=self.content_data["content_text"],
            scheduled_time=self.content_data["scheduled_time"]
        )
        
        scheduled_content = ScheduledContent.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(scheduled_content, "Scheduled content not found in database.")
        self.assertEqual(scheduled_content.content_text, self.content_data["content_text"])
        self.assertEqual(scheduled_content.scheduled_time, self.content_data["scheduled_time"])
        self.assertEqual(response, "Content scheduled successfully")

    def test_send_content_reminder(self):
        """
        Test that a reminder is sent to the user at the correct scheduled time.
        """
        send_content_reminder(self.scheduled_content.id)

        # Verify if a reminder notification was created
        reminder = Notification.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(reminder, "Reminder notification not sent.")
        self.assertEqual(reminder.message, f"Reminder: Scheduled content '{self.scheduled_content.content_text}' is due now.")
    
    def test_schedule_content_in_past(self):
        """
        Test that scheduling content in the past returns an error.
        """
        past_time = datetime.now() - timedelta(hours=1)
        response = schedule_content(
            user_id=self.user.id,
            content_text="Past content test",
            scheduled_time=past_time
        )
        self.assertEqual(response, "Scheduled time cannot be in the past")

    def test_schedule_duplicate_content(self):
        """
        Test that duplicate content scheduling with the same text and time is prevented.
        """
        duplicate_content = schedule_content(
            user_id=self.user.id,
            content_text=self.content_data["content_text"],
            scheduled_time=self.content_data["scheduled_time"]
        )
        self.assertEqual(duplicate_content, "Content already scheduled at this time")
    
    def test_schedule_content_without_user(self):
        """
        Test that attempting to schedule content without a valid user ID raises an error.
        """
        response = schedule_content(
            user_id=None,
            content_text="Invalid user test",
            scheduled_time=self.scheduled_time
        )
        self.assertEqual(response, "Invalid user ID provided")

if __name__ == '__main__':
    unittest.main()
