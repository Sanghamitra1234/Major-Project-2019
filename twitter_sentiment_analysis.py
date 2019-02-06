import tweepy
import pandas as pd
import sys
import csv
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
api = tweepy.API(auth)

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
print(places[0].id)

# search tweets with some keywords
results = api.search('hash_tag',
                     count=number,
                     tweet_mode='extended',
                     lang='en',
                     place=places[0].id
                     )

tweets = results
data = pd.DataFrame(data=[tweet.full_text for tweet in tweets], columns=['Tweets'])

# print the first 10 data
print(data.head(10))

import nltk
nltk.download('vader_lexicon')

sid = SentimentIntensityAnalyzer()


l = []
counter = Counter()

for index, row in data.iterrows():
    ss = sid.polarity_scores(row["Tweets"])
    l.append(ss)
    k = ss['compound']
    if k >= 0.05:
        counter['positive'] += 1
    elif k <= -0.05:
        counter['negative'] += 1
    else:
        counter['neutral'] += 1

se = pd.Series(l)
data['polarity'] = se.values
# to print in tabular form
print(data.head(100))

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
