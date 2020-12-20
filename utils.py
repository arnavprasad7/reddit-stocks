import praw 
import json
import pandas as pd

from datetime import datetime

import numpy as np

from textblob import TextBlob

from nltk.tokenize import word_tokenize


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