import praw 
import json
import pandas as pd

from nltk.tokenize import word_tokenize


def get_posts(reddit, subreddit, limit=20, title_conditions=[""]):
    """
    Get data from the "hot" posts from a particualar subreddit.

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

                posts.append(post)   

    return posts