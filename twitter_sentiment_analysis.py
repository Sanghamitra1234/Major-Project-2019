import tweepy
import pandas as pd
import sys
import csv
import pickle
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from collections import Counter

if sys.version_info[0] < 3:
    input = raw_input

# importing the auth variables from secret.py
import secret

# authenicating with authentication variables
auth = tweepy.OAuthHandler(secret.consumer_key, secret.consumer_secret)
auth.set_access_token(secret.access_token, secret.access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
# Error handling
if (not api):
    print("Problem Connecting to API")

# inputs for counts taken
hash_tag = input("Which party you want to search ? \n")
number = int(input("How many Tweets do you want to analyze? \n"))
location = input("What is the location of party? \n")

# Getting Geo ID for Places
places = api.geo_search(query=location)
# place id
print(places[0])

tweetsPerQry = 100  # this is the max the API permits


# If results from a specific ID onwards are reqd, set since_id to that ID.
# else default to no lower limit, go as far back as API allows
sinceId = None

# If results only below a specific ID are, set max_id to that ID.
# else default to no upper limit, start from the most recent tweet matching the search query.
max_id = -1
data = None

dataset = []
outputFile = 'test.data'
fw = open(outputFile, 'wb')

tweetCount = 0
print("Downloading max {0} tweets".format(number))
while tweetCount < number:
    try:
        if (max_id <= 0):
            if (not sinceId):
                new_tweets = api.search(q=hash_tag, count=tweetsPerQry, tweet_mode='extended', lang='en')
                tweetCount += len(new_tweets)
                print("Downloaded {0} tweets".format(tweetCount))
            else:
                new_tweets = api.search(q=hash_tag, count=tweetsPerQry,
                                        since_id=sinceId, tweet_mode='extended', lang='en')
                print("here 2")
        else:
            if (not sinceId):
                new_tweets = api.search(q=hash_tag, count=tweetsPerQry,
                                        max_id=str(max_id - 1), tweet_mode='extended', lang='en')
                print("here 3")
            else:
                new_tweets = api.search(q=hash_tag, count=tweetsPerQry,
                                        max_id=str(max_id - 1),
                                        since_id=sinceId, tweet_mode='extended', lang='en')
                print("here 4")
            if not new_tweets:
                print("No more tweets found")
                break

        # print(new_tweets)

        tweets = new_tweets
        for tweet in tweets:
            dataset.append(tweet.full_text)
        #data += pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        tweetCount += len(new_tweets)
        print("Downloaded {0} tweets".format(tweetCount))
        max_id = new_tweets[-1].id
    except tweepy.TweepError as e:
        print(str(e))
        break


pickle.dump(dataset, fw)
fw.close()

inputFile = 'test.data'
fd = open(inputFile, 'rb')
dataset = pickle.load(fd)
print(dataset)

# search tweets with some keywords
# results = api.search(hash_tag,
#                      count=number,
#                      since="2019-03-04",
# 					 until="2019-03-05",
#                      tweet_mode='extended',
#                      lang='en',
#                      place=places[0].id
#                      )

# print (results)

# tweets = results
# data = pd.DataFrame(data=[tweet.full_text for tweet in tweets], columns=['Tweets'])
# data.to_csv('output.csv')

# print the first 10 data
# print(data)

import nltk
nltk.download('vader_lexicon')

sid = SentimentIntensityAnalyzer()


l = []
counter = Counter()

for data in dataset:
    ss = sid.polarity_scores(data)
    l.append(ss)
    k = ss['compound']
    if k >= 0.05:
        counter['positive'] += 1
    elif k <= -0.05:
        counter['negative'] += 1
    else:
        counter['neutral'] += 1

positive = counter['positive']
negative = counter['negative']
neutral = counter['neutral']

colors = ['green', 'red', 'grey']
sizes = [positive, negative, neutral]
labels = 'Positive', 'Negative', 'Neutral'

# use matplotlib to plot the chart
plt.pie(
    x=sizes,
    shadow=True,
    colors=colors,
    labels=labels,
    startangle=90,
    autopct='%.1f%%'
)

plt.title("Sentiment of {} Tweets about {}".format(number, hash_tag))
plt.show()
