import sys
from typing import Dict
import unittest
from unittest.mock import patch

print(sys.path)
from clients.deviant import SUBMIT_URL, TOKEN_URL, UPLOAD_URL, DeviantClient
import requests_mock


def get_fake_config(partial: Dict[str, any] = {}):
    config = {"client_id": 123, "client_secret": 456, "default_mature_classification": "", "refresh_token": "111"}
    config.update(partial)
    return config


@patch("builtins.open")
def test_post_image_successfully():
    with requests_mock.Mocker() as req_mock:
        req_mock.post(TOKEN_URL, json={"refresh_token": "12345", "access_token": "acc123"})
        req_mock.post(UPLOAD_URL, json={"itemid": "1"})
        req_mock.post(SUBMIT_URL, json={})
        client = DeviantClient("test", get_fake_config())

        assert client.schedule("tests/fixtures/fake.jpg", "some caption") == True


def test_post_image_successfully_writes_refresh_token():
    with requests_mock.Mocker() as req_mock:
        req_mock.post(TOKEN_URL, json={"refresh_token": "12345", "access_token": "acc123"})
        req_mock.post(UPLOAD_URL, json={"itemid": "1"})
        req_mock.post(SUBMIT_URL, json={})

        with patch("builtins.open", unittest.mock.mock_open(read_data="12345")) as mock_open:
            DeviantClient("test", get_fake_config()).schedule("tests/fixtures/fake.jpg", "some caption")
            mock_open.assert_called_once_with("foo", "rw")
