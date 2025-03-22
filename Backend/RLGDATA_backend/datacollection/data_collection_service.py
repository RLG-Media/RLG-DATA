# data_collection_service.py
import tweepy
import facebook
import time
from kafka import KafkaProducer
import json
import os

# Twitter API credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Facebook API credentials
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'social_media_data'

class DataCollectionService:
    def __init__(self):
        self.twitter_api = self.setup_twitter_api()
        self.facebook_api = self.setup_facebook_api()
        self.kafka_producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER],
                                            value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def setup_twitter_api(self):
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        return tweepy.API(auth)

    def setup_facebook_api(self):
        return facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN, version="3.0")

    def collect_twitter_data(self, keyword):
        tweets = self.twitter_api.search(q=keyword, count=100)
        for tweet in tweets:
            data = {
                'platform': 'twitter',
                'text': tweet.text,
                'user': tweet.user.screen_name,
                'created_at': str(tweet.created_at),
                'keyword': keyword
            }
            self.kafka_producer.send(KAFKA_TOPIC, value=data)

    def collect_facebook_data(self, keyword):
        posts = self.facebook_api.request(f'/search?q={keyword}&type=post')
        for post in posts['data']:
            data = {
                'platform': 'facebook',
                'text': post.get('message', ''),
                'user': post['from']['name'],
                'created_at': post['created_time'],
                'keyword': keyword
            }
            self.kafka_producer.send(KAFKA_TOPIC, value=data)

    def run(self, keywords):
        while True:
            for keyword in keywords:
                try:
                    self.collect_twitter_data(keyword)
                    self.collect_facebook_data(keyword)
                except Exception as e:
                    print(f"Error collecting data for keyword {keyword}: {str(e)}")
            time.sleep(300)  # Wait for 5 minutes before next round of collection

if __name__ == "__main__":
    service = DataCollectionService()
    service.run(['python', 'data science', 'machine learning'])  # Example keywords