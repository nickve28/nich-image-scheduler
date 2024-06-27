from typing import Dict
import unittest
from unittest.mock import mock_open, patch
import uuid

from models.account import Account
from src.deviant_utils.deviant_refresh_token import get_refresh_token

from src.clients.deviant import SUBMIT_URL, TOKEN_URL, UPLOAD_URL, DeviantClient
import requests_mock


def get_fake_account(partial: Dict[str, any] = {}):
    config = {
        "id": "test",
        "directory_path": ".",
        "extensions": ["jpg"],
        "platforms": ["Deviant"],
        "deviant": {"client_id": 123, "client_secret": 456, "default_mature_classification": ""},
        "nsfw": False,
    }

    if "deviant_config" in partial:
        config["deviant_config"].update(partial["deviant_config"])
        config.update(partial)
    if "nsfw" in partial:
        config["nsfw"] = partial["nsfw"]
    return Account(config)


class TestDeviantClient(unittest.TestCase):
    def test_post_image_successfully(self):
        with requests_mock.Mocker() as req_mock:
            req_mock.post(TOKEN_URL, json={"refresh_token": "12345", "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={})
            client = DeviantClient(get_fake_account())

            assert client.schedule("tests/fixtures/fake.jpg", "some caption") == True

    def test_post_image_successfully_writes_refresh_token(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account()).schedule("tests/fixtures/fake.jpg", "some caption")

            assert get_refresh_token("test") == random_token

    def test_post_image_passes_the_access_token_to_the_upload_request(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account()).schedule("tests/fixtures/fake.jpg", "some caption")

            self.assertEqual(req_mock.request_history[1].headers["Authorization"], "Bearer acc123")

    def test_post_image_passes_the_access_token_to_the_publish_request(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account()).schedule("tests/fixtures/fake.jpg", "some caption")

            self.assertEqual(req_mock.request_history[2].headers["Authorization"], "Bearer acc123")

    def test_post_image_sends_correct_payload_to_submit(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "itemid1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account()).schedule("tests/fixtures/fake.jpg", "some caption")

            expected = "itemid=itemid1&title=some+caption&artist_comments=&is_mature=false&is_ai_generated=true&allow_free_download=false&tags="
            self.assertEqual(req_mock.request_history[2].text, expected)

    def test_post_image_sends_correct_payload_to_submit_with_nsfw_on(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "itemid1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account({"nsfw": True})).schedule("tests/fixtures/fake.jpg", "some caption")

            expected = "itemid=itemid1&title=some+caption&artist_comments=&is_mature=true&is_ai_generated=true&allow_free_download=false&tags="
            self.assertEqual(req_mock.request_history[2].text, expected)
