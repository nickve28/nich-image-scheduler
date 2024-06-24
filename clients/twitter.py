import tweepy
import os
import random
import sys
import shutil

from utils.text_utils import to_cursive

directory_path = os.getenv('DIRECTORY_PATH')
extensions = os.getenv('EXTENSIONS').split(',')

BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

tags = [ "#AIart", "#AIイラスト", "#AIArtwork", "#AIArtCommunity", "#AIArtGallery", "#AIArtworks", "#AIgirls" ]
if os.getenv('TWITTER_TAGS') is not None:
    tags = os.getenv('TWITTER_TAGS').split(",")

def decorate_caption(caption):
    make_cursive = os.getenv('TWITTER_FONT_CURSIVE', '0') == '1'
    return to_cursive(caption) if make_cursive else caption

def add_tags(caption):
    combined_tags = " ".join(random.sample(tags, 2))
    if os.getenv('TWITTER_TAGS_BEFORE_CAPTION', '0') == '1':
      return f'{combined_tags} {caption}'
    return f'{caption} {combined_tags}'

def schedule(image_path, json_path, caption):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    old_client = tweepy.API(auth, wait_on_rate_limit=True)

    client = tweepy.Client(
        BEARER_TOKEN,
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )

    try:
        tweet_text = add_tags(decorate_caption(caption))
        print(f'uploading: {image_path}')
        media_id = old_client.media_upload(filename=image_path).media_id_string
        print(f'uploaded: {media_id}')

        
        print(f'tweeting: {tweet_text}')
        response = client.create_tweet(text=tweet_text, media_ids=[media_id])

        print(f'tweeted! response: {response}')
        print(f'https://twitter.com/user/status/{response.data["id"]}')
        return True

    except tweepy.errors.TweepyException as e:
        print(f'Failed to tweet: {e}')
        return False