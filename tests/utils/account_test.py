from typing import Dict
import unittest
from models.account import Account
from utils.account_loader import load_accounts, select_account, parse_account

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
        "deviant_config": {"client_id": 123, "client_secret": 456, "default_mature_classification": "", "refresh_token": None, "featured": True},
    }
    config.update(partial)
    return config


def sample_deviant_config():
    return {"client_id": "c1", "client_secret": "c2", "featured": True}


class TestAccount(unittest.TestCase):
    def test_loads_accounts_successfully(self):
        self.assertIsInstance(load_accounts(path), Dict)

    def test_select_account_makes_class(self):
        self.assertIsInstance(select_account("my_account", path), Account)

    def test_account_contains_id(self):
        result = select_account("my_account", path)
        self.assertEqual(result.id, "my_account")

    def test_account_defaults_nsfw_to_false(self):
        config = sample_config()
        del config["nsfw"]
        result = parse_account(config)
        self.assertEqual(result.nsfw, False)

    def test_account_allows_configuring_nsfw(self):
        config = sample_config({"nsfw": True})
        result = parse_account(config)
        self.assertEqual(result.nsfw, True)

    def test_loads_deviant_refresh_token(self):

        config = sample_config({"nsfw": True, "id": "test_account", "deviant": sample_deviant_config()})
        result = parse_account(config)
        self.assertEqual(result.deviant_config.refresh_token, "12345")

    def test_omits_deviant_token_if_not_found(self):
        config = sample_config({"nsfw": True, "id": "test_account2", "deviant": sample_deviant_config()})
        result = parse_account(config)
        self.assertEqual(result.deviant_config.refresh_token, None)

    def test_sets_deviant_featured(self):
        config = sample_config({"nsfw": True, "id": "test_account2", "deviant": sample_deviant_config()})
        result = parse_account(config)
        self.assertEqual(result.deviant_config.featured, True)

    def test_sets_deviant_featured_true_by_default(self):
        deviant = sample_deviant_config()
        del deviant["featured"]
        config = sample_config({"nsfw": True, "id": "test_account2", "deviant": deviant})
        result = parse_account(config)
        self.assertEqual(result.deviant_config.featured, True)

    def test_sets_deviant_galleries_empty_by_default(self):
        config = sample_config({"nsfw": True, "id": "test_account2", "deviant": sample_deviant_config()})
        result = parse_account(config)
        self.assertEqual(result.deviant_config.gallery_ids, [])
