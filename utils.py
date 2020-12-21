import praw 
import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from textblob import TextBlob
from nltk.tokenize import word_tokenize
import requests
import traceback
import time


def get_posts(reddit, subreddit, limit=20, title_conditions=[""]):
    """
    Get data from the "hot" posts from a particular subreddit.

    Inputs:
    - reddit: PRAW reddit instance
    - subreddit: subreddit name
    - limit: how many posts you want
    - title_conditions: list of words that should be in post titles (will get all posts by default)

    Outputs:
    -posts: list of dictionaries, where each element corresponds to a single post and contains the following keys:
        - "title"
        - "id"
        - "comments"
        - "time"
    """

    subreddit = reddit.subreddit(subreddit)

    submissions = subreddit.hot(limit=20)

    posts = []

    for submission in submissions:
        for word in title_conditions:
            if word in submission.title:
                post = {}

                post["title"] = submission.title
                post["id"] = submission.id
                post["comments"] = submission.comments
                post["time"] = datetime.fromtimestamp(submission.created_utc)

                posts.append(post)   

    return posts

def getPolarity(text):
    return TextBlob(text).sentiment.polarity

def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def sentiment_score(x):
    """
    Input:
    - mean of weighted polarities (any real number, positive or negative)

    Output:
    - Weighted sentiment score, mapped between [-1, 1], corresponding to negative or positive responses
    """
    
    if x >= 0:
        score = 1 - np.exp(-x)
    else:
        score = np.exp(x) - 1

    return score

def date_to_utc(date):
    """
    Input:
    - datetime object

    Output:
    - Date in UTC
    """

    date = str(date)

    return int(time.mktime(datetime.strptime(date, "%Y-%m-%d").timetuple()))




def download_from_pushshift(output_filename, object_type, chosen_subreddit, date):
    #Print that code is starting
    print(f"Saving {object_type}s to {output_filename}")
    
    #Template URL for using pushshift
    url = "https://api.pushshift.io/reddit/{}/search?limit=1000&sort_type=score&sort=desc&subreddit={}&after={}&before={}"
    
    subreddit = chosen_subreddit

    #Convert date from string to unix time
    day = int(time.mktime(datetime.strptime(date, "%Y-%m-%d").timetuple()))
    
    count = 0
    handle = open(output_filename, 'a')
    
    #Generate the URL we will use to search reddit
    formatted_url = url.format(object_type, subreddit, str(day), str(day + 86400)) #set limit to be 24 hours after start time
    json = requests.get(formatted_url, headers={'User-Agent': "Post downloader by /u/Watchful1"})
    time.sleep(1) # avoid pushshift rate limit
    
    try:
        json_data = json.json()
    
        objects = json_data['data']
        
        handle.write("DATE: " + date + "\n\n----------------------\n\n")
        
        for object in objects:
            count += 1
            if object_type == 'comment':
                try:
                    handle.write(str(object['score']))
                    #handle.write(" : ")
                    #handle.write(datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d"))
                    handle.write("\n")
                    text = object['body']
                    textASCII = text.encode(encoding='ascii', errors='ignore').decode()
                    handle.write(textASCII)
                    handle.write("\n-------------------------------\n")
                except Exception as err:
                    print(f"Couldn't print comment: https://www.reddit.com{object['permalink']}")
                    print(traceback.format_exc())
            elif object_type == 'submission':
                try:
                    handle.write(str(object['score']))
                    #handle.write(" : ")
                    #handle.write(datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d"))
                    handle.write("\n")
                    text = object['title']
                    if len(object['selftext']) > 0:
                        text += " - " 
                        text += object['selftext']
                    textASCII = text.encode(encoding='ascii', errors='ignore').decode()
                    handle.write(textASCII)
                    handle.write("\n-------------------------------\n")
                except Exception as err:
                    print(f"Couldn't print post: {object['url']}")
                    print(traceback.format_exc())
        
        
        handle.write("\n\n\n\n\n\n\n")
    except:
        print("Error: No {}s found on {}".format(object_type, date))
    
    
    print("Saved {} {}s from {}".format(count, object_type, datetime.fromtimestamp(day).strftime("%Y-%m-%d")))
    handle.close()
   

def create_url(subreddit, date):
    """
    Inputs:
    - subreddit: name of subreddit
    - date: datetime object for required day

    Output:
    - formatted_url: in the pushshift request format
    """

    before = date.date()

    after = (date + timedelta(days=1)).date()

    #Template URL for using pushshift
    url = "https://api.pushshift.io/reddit/{}/search?limit=1000&sort_type=score&sort=desc&subreddit={}&after={}&before={}"

    formatted_url = url.format("comment", subreddit, date_to_utc(before), date_to_utc(after))

    return formatted_url






