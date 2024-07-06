from collections import namedtuple
import os
import random
from typing import Dict
import unittest
from unittest.mock import Mock, patch
import uuid
from schedule_image import execute
from utils.account_loader import select_account
from utils.image_metadata_adjuster import ImageMetadataAdjuster
import tweepy
import requests_mock
from src.clients.deviant import SUBMIT_URL, TOKEN_URL, UPLOAD_URL

path = "tests/fixtures"

TweetResponse = namedtuple("TweetResponse", ["data"])
MediaResponse = namedtuple("MediaResponse", ["media_id_string"])


class IntegrationTestScheduleImage(unittest.TestCase):
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

    def test_schedules_twitter_successfully(self):
        account = select_account("my_account", path)

        with (
            patch("tweepy.OAuthHandler", return_value=self.mock_oauth_handler),
            patch("tweepy.API", return_value=self.mock_api),
            patch("tweepy.Client", return_value=self.mock_client),
            patch("os.rename"),
        ):
            result = execute(account, "Twitter")
            self.assertEqual(TweetResponse(data={"id": "123"}), result)

    def test_schedules_twitter_and_renames_file(self):
        account = select_account("my_account", path)

        with (
            patch("tweepy.OAuthHandler", return_value=self.mock_oauth_handler),
            patch("tweepy.API", return_value=self.mock_api),
            patch("tweepy.Client", return_value=self.mock_client),
            patch("os.rename") as mock_rename,
        ):
            execute(account, "Twitter")
            expected_path = os.path.abspath("./tests/fixtures")
            expected_origin_file = os.path.join(expected_path, "test_TWIT_Q.jpg")
            expected_destination_file = os.path.join(expected_path, "test_TWIT_P.jpg")
            mock_rename.assert_called_once_with(expected_origin_file, expected_destination_file)

    def test_schedules_deviant_successfully(self):
        account = select_account("my_account", path)

        with requests_mock.Mocker() as req_mock, patch("os.rename"):
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={"id": "123"})

            result = execute(account, "Deviant")
            self.assertEqual({"id": "123"}, result)

    def test_schedules_deviant_and_renames_files(self):
        account = select_account("my_account", path)

        with requests_mock.Mocker() as req_mock, patch("os.rename") as mock_rename:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={"id": "123"})

            execute(account, "Deviant")
            expected_path = os.path.abspath("./tests/fixtures")
            expected_origin_file = os.path.join(expected_path, "test_DEVI_Q.jpg")
            expected_destination_file = os.path.join(expected_path, "test_DEVI_P.jpg")
            mock_rename.assert_called_once_with(expected_origin_file, expected_destination_file)
