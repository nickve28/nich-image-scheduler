from collections import namedtuple
import random
from typing import Dict
import unittest
from unittest.mock import Mock, mock_open, patch
import tweepy

from clients.twitter import TwitterClient


def get_fake_config(partial: Dict[str, any] = {}):
    config = {
        "client_id": 123,
        "client_secret": 456,
        "consumer_key": "c1",
        "consumer_secret": "c2",
        "access_token": "a1",
        "access_token_secret": "a2",
        "bearer_token": "b1",
    }
    config.update(partial)
    return config


TweetResponse = namedtuple("TweetResponse", ["data"])
MediaResponse = namedtuple("MediaResponse", ["media_id_string"])


class TestTwitterClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.random_state = random.getstate()
        random.seed(42)
        mock_oauth_handler = Mock(spec=tweepy.OAuthHandler)
        mock_api = Mock(spec=tweepy.API)
        mock_client = Mock(spec=tweepy.Client)

        mock_tweet_data = {"id": "123"}
        mock_client.create_tweet.return_value = TweetResponse(data=mock_tweet_data)
        mock_api.media_upload.return_value = MediaResponse(media_id_string="1")

        cls.mock_oauth_handler = mock_oauth_handler
        cls.mock_api = mock_api
        cls.mock_client = mock_client

    @classmethod
    def tearDownClass(cls) -> None:
        random.setstate(cls.random_state)

    def setUp(self):
        # Reset the state of the mocks before each test
        self.mock_oauth_handler.reset_mock()
        self.mock_api.reset_mock()
        self.mock_client.reset_mock()

    def test_post_image_successfully(self):
        with patch("tweepy.OAuthHandler", return_value=self.mock_oauth_handler), patch("tweepy.API", return_value=self.mock_api), patch(
            "tweepy.Client", return_value=self.mock_client
        ):
            client = TwitterClient(get_fake_config())
            assert client.schedule("tests/fixtures/fake.jpg", "some caption") == True

    def test_post_with_cursive_text(self):
        with patch("tweepy.OAuthHandler", return_value=self.mock_oauth_handler), patch("tweepy.API", return_value=self.mock_api), patch(
            "tweepy.Client", return_value=self.mock_client
        ):
            client = TwitterClient(get_fake_config({"cursive_font": True}))
            client.schedule("tests/fixtures/fake.jpg", "some caption")
            self.mock_client.create_tweet.assert_called_once_with(text="𝑠𝑜𝑚𝑒 𝑐𝑎𝑝𝑡𝑖𝑜𝑛 #AIart #AIArtworks", media_ids=["1"])

    def test_post_with_prepended_text(self):
        with patch("tweepy.OAuthHandler", return_value=self.mock_oauth_handler), patch("tweepy.API", return_value=self.mock_api), patch(
            "tweepy.Client", return_value=self.mock_client
        ):
            client = TwitterClient(get_fake_config({"tag_position": "prepend"}))
            client.schedule("tests/fixtures/fake.jpg", "some caption")
            self.mock_client.create_tweet.assert_called_once_with(text="#AIイラスト #AIArtworks some caption", media_ids=["1"])

    def test_post_with_custom_tag_count(self):
        with patch("tweepy.OAuthHandler", return_value=self.mock_oauth_handler), patch("tweepy.API", return_value=self.mock_api), patch(
            "tweepy.Client", return_value=self.mock_client
        ):
            client = TwitterClient(get_fake_config({"tag_count": 3}))
            client.schedule("tests/fixtures/fake.jpg", "some caption")
            self.mock_client.create_tweet.assert_called_once_with(text="some caption #AIArtwork #AIイラスト #AIArtworks", media_ids=["1"])
