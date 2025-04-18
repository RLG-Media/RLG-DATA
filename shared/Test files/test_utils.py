import os
import json
from datetime import datetime
import random

class TestUtils:
    def __init__(self, base_dir="tests"):
        self.base_dir = base_dir
    
    def load_test_data(self, filename="test_data.json"):
        """ Load test data from a JSON file """
        try:
            with open(os.path.join(self.base_dir, filename), 'r') as file:
                data = json.load(file)
            return data
        except Exception as e:
            raise FileNotFoundError(f"Error loading test data file: {str(e)}")
    
    def save_test_data(self, data, filename="test_output.json"):
        """ Save test data to a JSON file """
        try:
            with open(os.path.join(self.base_dir, filename), 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Test data saved to {filename}")
        except Exception as e:
            print(f"Error saving test data file: {str(e)}")
    
    def generate_test_report(self, test_results, filename="test_report.txt"):
        """ Generate a test report from the results """
        try:
            with open(os.path.join(self.base_dir, filename), 'w') as file:
                file.write("Test Report\n")
                file.write("="*40 + "\n")
                file.write(f"Generated on: {datetime.now()}\n\n")
                file.write("Test Results:\n")
                for result in test_results:
                    file.write(f"Test Case: {result['test_case']}\n")
                    file.write(f"Status: {result['status']}\n")
                    file.write(f"Details: {result['details']}\n\n")
            print(f"Test report saved to {filename}")
        except Exception as e:
            print(f"Error generating test report: {str(e)}")

    def compare_data(self, expected, actual):
        """ Compare two sets of data and return the differences """
        differences = []
        for key in expected.keys():
            if key in actual:
                if expected[key] != actual[key]:
                    differences.append(f"Mismatch at {key}: Expected {expected[key]}, but got {actual[key]}")
            else:
                differences.append(f"Missing key: {key} in actual data")
        return differences

    def generate_test_data_summary(self, data):
        """ Generate a summary from the test data """
        summary = {
            "total_users": len(data["users"]),
            "total_fans": len(data["fans"]),
            "total_posts": len(data["posts"]),
            "total_comments": len(data["comments"]),
            "total_likes": len(data["likes"]),
            "total_subscriptions": len(data["subscriptions"]),
        }
        return summary

    def validate_data_format(self, data):
        """ Validate the structure and format of test data """
        required_fields_user = {"user_id", "name", "email", "username", "created_at", "status"}
        required_fields_fan = {"fan_id", "name", "email", "subscription_plan", "created_at", "status"}
        required_fields_post = {"post_id", "user_id", "content", "media_url", "tags", "created_at", "likes"}
        required_fields_comment = {"comment_id", "user_id", "post_id", "content", "created_at", "likes"}
        required_fields_like = {"like_id", "user_id", "post_id", "created_at"}
        required_fields_subscription = {"subscription_id", "fan_id", "plan", "start_date", "end_date"}

        errors = []
        
        for user in data["users"]:
            if not all(field in user for field in required_fields_user):
                errors.append(f"User data missing required fields: {user}")
        
        for fan in data["fans"]:
            if not all(field in fan for field in required_fields_fan):
                errors.append(f"Fan data missing required fields: {fan}")
        
        for post in data["posts"]:
            if not all(field in post for field in required_fields_post):
                errors.append(f"Post data missing required fields: {post}")
        
        for comment in data["comments"]:
            if not all(field in comment for field in required_fields_comment):
                errors.append(f"Comment data missing required fields: {comment}")
        
        for like in data["likes"]:
            if not all(field in like for field in required_fields_like):
                errors.append(f"Like data missing required fields: {like}")
        
        for subscription in data["subscriptions"]:
            if not all(field in subscription for field in required_fields_subscription):
                errors.append(f"Subscription data missing required fields: {subscription}")

        return errors if errors else None

    def generate_fake_user(self):
        """ Generate a single fake user for testing purposes """
        fake_user = {
            "user_id": ''.join(random.choices(string.ascii_letters, k=8)),
            "name": fake.name(),
            "email": fake.email(),
            "username": ''.join(random.choices(string.ascii_letters + string.digits, k=12)),
            "created_at": fake.date_time_this_year(),
            "status": random.choice(["active", "inactive"]),
        }
        return fake_user

    def generate_fake_fan(self, fan_id):
        """ Generate a single fake fan for testing purposes """
        fake_fan = {
            "fan_id": fan_id,
            "name": fake.name(),
            "email": fake.email(),
            "subscription_plan": random.choice(["basic", "premium", "vip"]),
            "created_at": fake.date_time_this_year(),
            "status": random.choice(["active", "inactive"]),
        }
        return fake_fan

    def generate_fake_post(self, user_id, fan_id):
        """ Generate a single fake post for testing purposes """
        fake_post = {
            "post_id": ''.join(random.choices(string.ascii_letters, k=8)),
            "user_id": user_id,
            "fan_id": fan_id,
            "content": fake.sentence(),
            "media_url": fake.image_url(),
            "tags": [self.generate_random_string(6) for _ in range(3)],
            "created_at": fake.date_time_this_year(),
            "likes": random.randint(0, 100),
            "comments": random.randint(0, 50),
            "shares": random.randint(0, 20),
        }
        return fake_post
    
    def generate_random_string(self, length=10):
        """ Helper function to generate a random string """
        return ''.join(random.choices(string.ascii_letters, k=length))
