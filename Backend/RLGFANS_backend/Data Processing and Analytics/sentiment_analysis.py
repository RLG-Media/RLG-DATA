# sentiment_analysis.py - Performs sentiment analysis on textual content for RLG Fans

from textblob import TextBlob
import logging

# Set up logging
logging.basicConfig(filename='sentiment_analysis.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s')


def analyze_sentiment(text):
    """
    Analyze the sentiment of a given text using TextBlob.
    
    Args:
        text (str): Text to be analyzed for sentiment.
        
    Returns:
        str: Sentiment classification ('positive', 'neutral', 'negative')
    """
    try:
        # Create a TextBlob object and analyze polarity
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Classify sentiment based on polarity
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        logging.info(f"Sentiment analyzed for text: '{text[:30]}...' - Sentiment: {sentiment}")
        return sentiment
    except Exception as e:
        logging.error(f"Sentiment analysis failed for text '{text[:30]}...': {str(e)}")
        return 'neutral'


def batch_analyze_sentiment(texts):
    """
    Analyze sentiment for a batch of texts.
    
    Args:
        texts (list): List of texts to be analyzed.
        
    Returns:
        list: List of sentiment classifications for each text.
    """
    try:
        sentiments = [analyze_sentiment(text) for text in texts]
        logging.info("Batch sentiment analysis completed successfully.")
        return sentiments
    except Exception as e:
        logging.error(f"Batch sentiment analysis failed: {str(e)}")
        return ['neutral'] * len(texts)
