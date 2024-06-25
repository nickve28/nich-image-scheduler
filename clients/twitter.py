import tweepy
import random

from utils.text_utils import to_cursive
from utils.account import TWITTER_DATA

BEARER_TOKEN = TWITTER_DATA['bearer_token']
CONSUMER_KEY = TWITTER_DATA['consumer_key']
CONSUMER_SECRET = TWITTER_DATA['consumer_secret']
ACCESS_TOKEN = TWITTER_DATA['access_token']
ACCESS_TOKEN_SECRET = TWITTER_DATA['access_token_secret']

DEFAULT_TAGS = [ "#AIart", "#AIイラスト", "#AIArtwork", "#AIArtCommunity", "#AIArtGallery", "#AIArtworks", "#AIgirls" ]
DEFAULT_TAG_COUNT = 2
tags = TWITTER_DATA.get('tags', DEFAULT_TAGS)
tag_count = TWITTER_DATA.get('tag_count', DEFAULT_TAG_COUNT)
tags_before_caption = TWITTER_DATA.get('tag_position', 'append') == 'prepend'

def decorate_caption(caption):
    make_cursive = TWITTER_DATA.get('cursive_font', False) is True
    return to_cursive(caption) if make_cursive else caption

def add_tags(caption):
    combined_tags = " ".join(random.sample(tags, tag_count))
    if tags_before_caption:
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