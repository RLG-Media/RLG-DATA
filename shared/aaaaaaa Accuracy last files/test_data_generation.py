import random
import string
import faker
from datetime import datetime, timedelta
import json

# Import models or necessary data structures for RLG Data and RLG Fans if required

# Initialize Faker for realistic data generation
fake = faker.Faker()

def generate_random_string(length=10):
    """ Generates a random string of fixed length """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def generate_random_number(min_val=1, max_val=100):
    """ Generates a random number within the specified range """
    return random.randint(min_val, max_val)

def generate_user_data():
    """ Generates sample user data """
    user_data = {
        "user_id": generate_random_string(8),
        "name": fake.name(),
        "email": fake.email(),
        "username": generate_random_string(12),
        "password": generate_random_string(16),
        "created_at": fake.date_time_this_year(),
        "last_login": fake.date_time_this_month(),
        "status": random.choice(["active", "inactive"]),
    }
    return user_data

def generate_fan_data(fan_id):
    """ Generates sample fan data for a given fan ID """
    fan_data = {
        "fan_id": fan_id,
        "name": fake.name(),
        "email": fake.email(),
        "subscription_plan": random.choice(["basic", "premium", "vip"]),
        "created_at": fake.date_time_this_year(),
        "last_interaction": fake.date_time_this_month(),
        "status": random.choice(["active", "inactive"]),
    }
    return fan_data

def generate_post_data(user_id, fan_id):
    """ Generates sample post data for users and fans """
    post_data = {
        "post_id": generate_random_string(8),
        "user_id": user_id,
        "fan_id": fan_id,
        "content": fake.sentence(),
        "media_url": fake.image_url(),
        "tags": [generate_random_string(6) for _ in range(3)],
        "created_at": fake.date_time_this_year(),
        "likes": generate_random_number(),
        "comments": generate_random_number(),
        "shares": generate_random_number(),
    }
    return post_data

def generate_comment_data(user_id, post_id):
    """ Generates sample comment data for posts """
    comment_data = {
        "comment_id": generate_random_string(8),
        "user_id": user_id,
        "post_id": post_id,
        "content": fake.text(max_nb_chars=100),
        "created_at": fake.date_time_this_year(),
        "likes": generate_random_number(),
    }
    return comment_data

def generate_like_data(user_id, post_id):
    """ Generates sample like data for posts """
    like_data = {
        "like_id": generate_random_string(8),
        "user_id": user_id,
        "post_id": post_id,
        "created_at": fake.date_time_this_year(),
    }
    return like_data

def generate_subscription_data(fan_id):
    """ Generates sample subscription data for fans """
    subscription_data = {
        "subscription_id": generate_random_string(8),
        "fan_id": fan_id,
        "plan": random.choice(["monthly", "quarterly", "yearly"]),
        "start_date": fake.date_this_year(),
        "end_date": fake.date_this_year() + timedelta(days=random.choice([30, 90, 365])),
        "amount": generate_random_number(10, 100),
    }
    return subscription_data

def generate_fake_data(num_users=100, num_fans=50, num_posts=200, num_comments=300, num_likes=400, num_subscriptions=50):
    """ Generates a large set of test data for various scenarios """
    all_data = {
        "users": [generate_user_data() for _ in range(num_users)],
        "fans": [generate_fan_data(fan_id=i) for i in range(num_fans)],
        "posts": [generate_post_data(user_id=generate_random_string(8), fan_id=generate_random_string(8)) for _ in range(num_posts)],
        "comments": [generate_comment_data(user_id=generate_random_string(8), post_id=generate_random_string(8)) for _ in range(num_comments)],
        "likes": [generate_like_data(user_id=generate_random_string(8), post_id=generate_random_string(8)) for _ in range(num_likes)],
        "subscriptions": [generate_subscription_data(fan_id=i) for i in range(num_subscriptions)]
    }
    return all_data

def save_data_to_file(data, filename="test_data.json"):
    """ Saves generated test data to a JSON file """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Generate test data
test_data = generate_fake_data()
save_data_to_file(test_data)
print("Test data has been generated and saved to test_data.json.")
