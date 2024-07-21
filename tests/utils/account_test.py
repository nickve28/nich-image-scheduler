from typing import Dict
import unittest
from models.account import Account
from utils.account_loader import load_accounts, select_account, parse_account

path = "tests/fixtures"


def sample_config(partial: Dict[str, any] = {}):
    config = {
        "id": "my_account",
        "directory_path": "./tests/fixtures",
        "extensions": ["jpg", "jpeg"],
        "platforms": ["Twitter", "Deviant"],
        "nsfw": False,
        "twitter": {
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
        "deviant": {
            "client_id": 123,
            "client_secret": 456,
            "default_mature_classification": "",
            "refresh_token": None,
            "featured": True,
        },
        "sub_configs": [
            {"directory_path": "./tests/fixtures/test", "nsfw": True, "deviant": {"default_mature_classification": "test", "featured": False}},
            {
                "directory_path": "./tests/fixtures/**/other",
                "deviant": {
                    "additional_gallery_ids": ["123"],
                    "featured": True,
                },
            },
        ],
    }
    config.update(partial)
    return config


def sample_deviant_config(partial={}):
    config = {"client_id": "c1", "client_secret": "c2", "featured": True}
    config.update(partial)
    return config


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

    def test_allows_updating_config_based_on_rules_and_file_path(self):
        config = sample_config({"nsfw": False, "id": "test_account2", "deviant": sample_deviant_config()})
        result = parse_account(config)
        result.set_config_for("./tests/fixtures/test/test.jpg")
        self.assertEqual(result.nsfw, True)
        self.assertEqual(result.deviant_config.featured, False)
        self.assertEqual(result.deviant_config.default_mature_classification, "test")

    def test_cascades_multiple_configs_on_multiple_matches(self):
        deviant_config = sample_deviant_config({"gallery_ids": ["1"]})
        config = sample_config({"nsfw": False, "id": "test_account2", "deviant": deviant_config})
        result = parse_account(config)
        result.set_config_for("./tests/fixtures/test/other/test.jpg")
        self.assertEqual(result.nsfw, True)
        self.assertEqual(result.deviant_config.featured, True)
        self.assertEqual(result.deviant_config.default_mature_classification, "test")
        self.assertEqual(result.deviant_config.gallery_ids, ["1", "123"])
