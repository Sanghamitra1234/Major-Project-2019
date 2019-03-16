from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask import Markup
import os

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'reds209ndsldssdsljdsldsdsljdsldksdksdsdfsfsfsfis'
#session.init_app(app)

positive = 0
negative = 0
neutral = 0


@app.route('/')
def home():
    if not session.get('searched'):
        return render_template('search.html')
    else:
        labels = ["Positive", "Negative", "Neutral"]
        global positive
        global negative
        global neutral
        values = [positive, negative, neutral]
        colors = ["#8bc34a", "#ff5252", "#9e9e9e"]
        session['searched'] = False
        return render_template('chart.html', set=zip(values, labels, colors))


@app.route('/search', methods=['POST'])
def do_search():
    if request.form['search_query'] == '':
        flash('Search Queary cannot be empty!')
        session['searched'] = False
    if request.form['max_tweets'] == '':
        flash('Max Tweets cannot be empty!')
        session['searched'] = False
    else:
        if not request.form['max_tweets'].isdigit():
            flash('Max Tweets should be a number!')
            session['searched'] = False
        else:
            if int(request.form['max_tweets']) > 0 & int(request.form['max_tweets']) <= 100000:
                import tweepy
                import sys
                import csv
                import pickle
                from nltk.sentiment.vader import SentimentIntensityAnalyzer
                from collections import Counter

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
                hash_tag = request.form['search_query']
                number = int(request.form['max_tweets'])
                # location = input("What is the location of party? \n")

                # # Getting Geo ID for Places
                # places = api.geo_search(query=location)
                # # place id
                # print(places[0])

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
                #                    until="2019-03-05",
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

                global positive
                positive = counter['positive']
                global negative
                negative = counter['negative']
                global neutral
                neutral = counter['neutral']
                session['searched'] = True
    return home()


app.secret_key = 'abcdefghijk'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)
