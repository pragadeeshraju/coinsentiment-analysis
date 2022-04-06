import tweepy
import sys
import datetime
import nltk
import os

twitter_secret=os.environ.get('TWITTER_SECRET')

nltk.download("stopwords")
nltk.download("punkt")
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")
from langdetect import detect
import numpy as np


def setupclient(secret):
    """Set up and return twitter client"""

    # with open(secretspath, "r") as secrets:
    #     api_secret = yaml.safe_load(secrets)
    client = tweepy.Client(secret)

    return client


def searchtweets(client, starttime, searchstring):
    """search for a string and return a list of cleaned tweets"""
    response = client.search_recent_tweets(
        searchstring,
        max_results=100,
    )
    tweets = response.data
    # cleaning:
    stopwords = nltk.corpus.stopwords.words("english")
    for tweet in tweets:
        if detect(tweet.text) != "en":
            tweets.remove(tweet)
        else:
            tokens = nltk.tokenize.word_tokenize(tweet.text)
            tokens_cleaned = [word for word in tokens if word.isalpha()]
            tokens_cleaned = [
                word for word in tokens_cleaned if word.lower() not in stopwords
            ]
            tweet.text = (" ").join(tokens_cleaned)

    return tweets


def getaveragesentiment(tweets):
    """for a list of tweets, get the average sentiment of each 
        tweet. 
    """
    
    tweetsentiment = 0
    sia = SentimentIntensityAnalyzer()
    for tweet in tweets:
        sentiment = sia.polarity_scores(tweet.text)
        tweetsentiment = tweetsentiment + sentiment["pos"] - sentiment["neg"]

    tweetsentiment = tweetsentiment / len(tweets)

    return tweetsentiment


def getpopularity(tweets, btc_tweets):
    """ for a list of tweets, return the popularity normalised 
        by bitcoin's popularity. popularity is measured by the 
        inverse of the amount of time between the first and 100th 
        tweet
    """

    btc_popularity = 1 / (btc_tweets[0].id - btc_tweets[-1].id)
    popularity = (1 / (tweets[0].id - tweets[-1].id)) / btc_popularity

    return popularity


def main():
    starttime = datetime.datetime.now() - datetime.timedelta(hours=2)
    client = setupclient(twitter_secret)
    clean_tweets = searchtweets(client, starttime, sys.argv[1])
    btc_tweets = searchtweets(client, starttime, "bitcoin")
    sentiment = getaveragesentiment(clean_tweets)
    popularity = getpopularity(clean_tweets)
    print(sentiment)
    print(popularity)


if __name__ == "__main__":
    main()