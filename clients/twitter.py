import tweepy
import os
import random
import sys
import shutil

directory_path = os.getenv('DIRECTORY_PATH')
extensions = os.getenv('EXTENSIONS').split(',')
mode = os.getenv('MODE')

BEARER_TOKEN = os.getenv('BEARER_TOKEN')
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

tags = [ "#AIart", "#AIイラスト", "#AIArtwork", "#AIArtCommunity", "#AIArtGallery", "#AIArtworks", "#AIgirls" ]

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
        print(f'uploading: {image_path}')
        media_id = old_client.media_upload(filename=image_path).media_id_string
        print(f'uploaded: {media_id}')

        tweet_text = f"{caption} {" ".join(random.sample(tags, 2))}"
        print(f'tweeting: {tweet_text}')
        response = client.create_tweet(text=tweet_text, media_ids=[media_id])

        print(f'tweeted! response: {response}')
        print(f'https://twitter.com/user/status/{response.data["id"]}')

        # tweeted_dir = os.path.join(directory, "tweeted")
        # if not os.path.exists(tweeted_dir):
        #     os.makedirs(tweeted_dir)

        # shutil.move(image_path, os.path.join(tweeted_dir, os.path.basename(image_path)))
        # print(f'Moved {os.path.basename(image_path)} to {tweeted_dir}')

        # if json_path:
        #     shutil.move(json_path, os.path.join(tweeted_dir, os.path.basename(json_path)))
        #     print(f'Moved {os.path.basename(json_path)} to {tweeted_dir}')

    except tweepy.errors.TweepyException as e:
        print(f'Failed to tweet: {e}')