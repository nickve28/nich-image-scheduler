from collections import namedtuple
import os
import sys
from typing import Dict
import unittest
from unittest.mock import Mock, mock_open, patch
import uuid
import pytest
import tweepy

from clients.twitter import TwitterClient
import requests_mock


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


class TestTwitterClient(unittest.TestCase):
    def test_post_image_successfully(self):
        mock_oauth_handler = Mock(spec=tweepy.OAuthHandler)
        mock_api = Mock(spec=tweepy.API)
        mock_client = Mock(spec=tweepy.Client)

        mock_tweet_data = {"id": "123"}
        mock_client.create_tweet.return_value = TweetResponse(data=mock_tweet_data)

        with patch("tweepy.OAuthHandler", return_value=mock_oauth_handler), patch("tweepy.API", return_value=mock_api), patch(
            "tweepy.Client", return_value=mock_client
        ):
            client = TwitterClient(get_fake_config())
            assert client.schedule("tests/fixtures/fake.jpg", "some caption") == True
