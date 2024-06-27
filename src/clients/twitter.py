import tweepy
import random

from utils.text_utils import to_cursive

DEFAULT_TAGS = [
    "#AIart",
    "#AIイラスト",
    "#AIArtwork",
    "#AIArtCommunity",
    "#AIArtGallery",
    "#AIArtworks",
    "#AIgirls",
]
DEFAULT_TAG_COUNT = 2
PREPEND = "prepend"


def decorate_caption(caption, opts):
    make_cursive = opts.get("cursive_font", False) is True
    return to_cursive(caption) if make_cursive else caption


def add_tags(caption, tags, tag_position, tag_count):
    combined_tags = " ".join(random.sample(tags, tag_count))
    if tag_position == PREPEND:
        return f"{combined_tags} {caption}"
    return f"{caption} {combined_tags}"


class TwitterClient:
    def __init__(self, config):
        self.config = config["twitter_config"]
        self.tags = self.config.get("tags", DEFAULT_TAGS)
        self.tag_count = self.config.get("tag_count", DEFAULT_TAG_COUNT)
        self.tag_position = self.config.get("tag_position", "append")

    def decorate_caption(self, caption):
        return add_tags(caption=decorate_caption(caption, self.config), tags=self.tags, tag_count=self.tag_count, tag_position=self.tag_position)

    def schedule(self, image_path, caption):
        config = self.config
        client = self.authenticate_api_client(config)
        media_client = self.authenticate_media_api_client(config)

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

    def authenticate_media_api_client(self, config):
        consumer_key = config["consumer_key"]
        consumer_secret = config["consumer_secret"]
        access_token = config["access_token"]
        access_token_secret = config["access_token_secret"]

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return tweepy.API(auth, wait_on_rate_limit=True)

    def authenticate_api_client(self, config):
        bearer_token = config["bearer_token"]
        consumer_key = config["consumer_key"]
        consumer_secret = config["consumer_secret"]
        access_token = config["access_token"]
        access_token_secret = config["access_token_secret"]

        return tweepy.Client(
            bearer_token,
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
            wait_on_rate_limit=True,
        )
