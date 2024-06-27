import tweepy
import random

from models.account import Account, TwitterPlatformConfig
from utils.text_utils import to_cursive


def decorate_caption(caption: str, config: TwitterPlatformConfig):
    return to_cursive(caption) if config.cursive_font else caption


def add_tags(caption: str, config: TwitterPlatformConfig):
    combined_tags = " ".join(random.sample(config.tags, config.tag_count))
    if config.tag_position == "prepend":
        return f"{combined_tags} {caption}"
    return f"{caption} {combined_tags}"


class TwitterClient:
    account: Account

    def __init__(self, account: Account):
        if not account.twitter_config:
            raise RuntimeError("No Deviant config found")
        self.account = account

    def decorate_caption(self, caption):
        twitter_config = self.account.twitter_config
        return add_tags(caption=decorate_caption(caption, twitter_config), config=twitter_config)

    def schedule(self, image_path, caption):
        client = self.authenticate_api_client()
        media_client = self.authenticate_media_api_client()

        try:
            tweet_text = self.decorate_caption(caption)
            print(f"uploading: {image_path}")
            print(f"tweeting: {tweet_text}")
            media_id = media_client.media_upload(filename=image_path).media_id_string
            print(f"uploaded: {media_id}")

            print(f"tweeting: {tweet_text}")
            response = client.create_tweet(text=tweet_text, media_ids=[media_id])

            print(f"tweeted! response: {response}")
            print(f'https://twitter.com/user/status/{response.data["id"]}')
            return True

        except tweepy.errors.TweepyException as e:
            print(f"Failed to tweet: {e}")
            return False

    def authenticate_media_api_client(self):
        twitter_config = self.account.twitter_config

        auth = tweepy.OAuthHandler(twitter_config.consumer_key, twitter_config.consumer_secret)
        auth.set_access_token(twitter_config.access_token, twitter_config.access_token_secret)
        return tweepy.API(auth, wait_on_rate_limit=True)

    def authenticate_api_client(self):
        twitter_config = self.account.twitter_config

        return tweepy.Client(
            twitter_config.bearer_token,
            twitter_config.consumer_key,
            twitter_config.consumer_secret,
            twitter_config.access_token,
            twitter_config.access_token_secret,
            wait_on_rate_limit=True,
        )
