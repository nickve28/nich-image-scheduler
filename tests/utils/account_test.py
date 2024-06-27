from typing import Dict
import unittest
from src.utils.account import load_accounts, select_account, parse_account

path = "tests/fixtures"


def sample_config(partial: Dict[str, any] = {}):
    config = {
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
    }
    config.update(partial)
    return config


class TestAccount(unittest.TestCase):
    def test_loads_accounts_successfully(self):
        self.assertIsInstance(load_accounts(path), Dict)

    def test_account_contains_all_keys(self):
        result = select_account("my_account", path)
        self.assertDictEqual(result, sample_config())

    def test_account_defaults_nsfw_to_false(self):
        config = sample_config()
        del config["nsfw"]
        result = parse_account(config)
        self.assertEqual(result["nsfw"], False)

    def test_account_allows_configuring_nsfw(self):
        config = sample_config({"nsfw": True})
        result = parse_account(config)
        self.assertEqual(result["nsfw"], True)

    def test_loads_deviant_refresh_token(self):
        config = sample_config({"nsfw": True, "id": "test_account", "deviant": {}})
        result = parse_account(config)
        self.assertEqual(result["deviant_config"]["refresh_token"], "12345")

    def test_omits_deviant_token_if_not_found(self):
        config = sample_config({"nsfw": True, "id": "test_account2", "deviant": {}})
        result = parse_account(config)
        self.assertEqual(result["deviant_config"]["refresh_token"], None)
