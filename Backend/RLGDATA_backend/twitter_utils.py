import tweepy

def create_twitter_api():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler('YOUR_API_KEY', 'YOUR_API_SECRET_KEY')
    auth.set_access_token('YOUR_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN_SECRET')

    api = tweepy.API(auth)
    return api

def get_tweets(keyword, count=100):
    api = create_twitter_api()
    tweets = api.search(q=keyword, count=count, tweet_mode='extended')
    return [{"text": tweet.full_text, "user": tweet.user.screen_name, "created_at": tweet.created_at} for tweet in tweets]
