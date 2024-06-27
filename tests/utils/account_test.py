from typing import Dict
import unittest
from unittest.mock import mock_open, patch

from src.utils.account import load_accounts, select_account

path = "tests/fixtures"


class TestAccount(unittest.TestCase):
    def test_loads_accounts_successfully(self):
        self.assertIsInstance(load_accounts(path), Dict)

    def test_account_contains_all_keys(self):
        self.maxDiff = None
        result = select_account("my_account", path)
        self.assertDictEqual(
            result,
            {
                "id": "my_account",
                "directory_path": "/my-pictures/**/posted",
                "extensions": ["jpg", "jpeg"],
                "platforms": ["Twitter", "Deviant"],
                "nsfw": False,
                "twitter_config": {
                    "consumer_key": "t123",
                    "consumer_secret": "t456",
                    "bearer_token": "AAAAAAAAAAAAAAAAAAAAA",
                    "access_token": "t111",
                    "access_token_secret": "t222",
                    "client_id": "t21",
                    "client_secret": "t22",
                    "cursive_font": True,
                    "tag_position": "prepend",
                    "tag_count": 2,
                    "tags": ["#AIart", "#AIArtwork", "#AIArtCommunity", "#AIArtGallery", "#AIArtworks"],
                },
                "deviant_config": {
                    "client_id": 123,
                    "client_secret": 456,
                    "default_mature_classification": "",
                    "refresh_token": None,
                    "galleries": {"featured": "Featured", "123": "My Galleria"},
                },
            },
        )
