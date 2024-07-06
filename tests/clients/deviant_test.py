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
        "deviant": {"client_id": 123, "client_secret": 456, "default_mature_classification": "", "featured": True},
        "nsfw": False,
    }

    if "deviant" in partial:
        config["deviant"].update(partial["deviant"])
    if "nsfw" in partial:
        config["nsfw"] = partial["nsfw"]

    return Account(config)


class TestDeviantClient(unittest.TestCase):
    def test_post_image_successfully(self):
        with requests_mock.Mocker() as req_mock:
            req_mock.post(TOKEN_URL, json={"refresh_token": "12345", "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={"id": "123"})
            client = DeviantClient(get_fake_account())

            assert client.schedule("tests/fixtures/test.jpg", "some caption") == {"id": "123"}

    def test_post_image_successfully_writes_refresh_token(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account()).schedule("tests/fixtures/test.jpg", "some caption")

            assert get_refresh_token("test") == random_token

    def test_post_image_passes_the_access_token_to_the_upload_request(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account()).schedule("tests/fixtures/test.jpg", "some caption")

            self.assertEqual(req_mock.request_history[1].headers["Authorization"], "Bearer acc123")

    def test_post_image_passes_the_access_token_to_the_publish_request(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account()).schedule("tests/fixtures/test.jpg", "some caption")

            self.assertEqual(req_mock.request_history[2].headers["Authorization"], "Bearer acc123")

    def test_post_image_sends_correct_payload_to_submit(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "itemid1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account()).schedule("tests/fixtures/test.jpg", "some caption")

            expected = "itemid=itemid1&title=some+caption&artist_comments=&is_mature=false&is_ai_generated=true&allow_free_download=false&display_resolution=0&feature=true&tags="
            self.assertEqual(req_mock.request_history[2].text, expected)

    def test_post_image_sends_correct_payload_to_submit_with_nsfw_on(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "itemid1"})
            req_mock.post(SUBMIT_URL, json={})

            DeviantClient(get_fake_account({"nsfw": True})).schedule("tests/fixtures/test.jpg", "some caption")

            expected = "itemid=itemid1&title=some+caption&artist_comments=&is_mature=true&is_ai_generated=true&allow_free_download=false&display_resolution=0&feature=true&tags="
            self.assertEqual(req_mock.request_history[2].text, expected)

    def test_post_image_sends_correct_payload_to_publish_with_gallery_id_set(self):
        with requests_mock.Mocker() as req_mock:
            random_token = str(uuid.uuid4())
            req_mock.post(TOKEN_URL, json={"refresh_token": random_token, "access_token": "acc123"})
            req_mock.post(UPLOAD_URL, json={"itemid": "itemid1"})
            req_mock.post(SUBMIT_URL, json={})

            account = get_fake_account({"deviant": {"gallery_ids": ["123", "456"], "featured": False}})
            DeviantClient(account).schedule("tests/fixtures/test.jpg", "some caption")

            expected_feature = "feature=false"
            expected_gallery_ids = "galleryids=123&galleryids=456"
            self.assertIn(expected_feature, req_mock.request_history[2].text)
            self.assertIn(expected_gallery_ids, req_mock.request_history[2].text)
