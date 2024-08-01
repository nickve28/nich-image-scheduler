from typing import Dict
import unittest
from models.account import Account
from utils.account_loader import load_accounts, select_account, parse_account
from factories.factories import config, deviant

path = "tests/fixtures"


class TestAccount(unittest.TestCase):
    def test_loads_accounts_successfully(self):
        self.assertIsInstance(load_accounts(path), Dict)

    def test_select_account_makes_class(self):
        self.assertIsInstance(select_account("my_account", path), Account)

    def test_account_contains_id(self):
        result = select_account("my_account", path)
        self.assertEqual(result.id, "my_account")

    def test_account_defaults_nsfw_to_false(self):
        test_config = config()
        del test_config["nsfw"]
        result = parse_account(test_config, [])
        self.assertEqual(result.nsfw, False)

    def test_account_allows_configuring_nsfw(self):
        test_config = config({"nsfw": True})
        result = parse_account(test_config, [])
        self.assertEqual(result.nsfw, True)

    def test_loads_deviant_refresh_token(self):
        test_config = config({"nsfw": True, "id": "test_account", "deviant": deviant()})
        result = parse_account(test_config, [])
        self.assertEqual(result.deviant_config.refresh_token, "12345")

    def test_omits_deviant_token_if_not_found(self):
        test_config = config({"nsfw": True, "id": "test_account2", "deviant": deviant()})
        result = parse_account(test_config, [])
        self.assertEqual(result.deviant_config.refresh_token, None)

    def test_sets_deviant_featured(self):
        test_config = config({"nsfw": True, "id": "test_account2", "deviant": deviant()})
        result = parse_account(test_config, [])
        self.assertEqual(result.deviant_config.featured, True)

    def test_sets_deviant_featured_true_by_default(self):
        deviant_config = deviant()
        del deviant_config["featured"]
        test_config = config({"nsfw": True, "id": "test_account2", "deviant": deviant_config})
        result = parse_account(test_config, [])
        self.assertEqual(result.deviant_config.featured, True)

    def test_sets_deviant_galleries_empty_by_default(self):
        test_config = config({"nsfw": True, "id": "test_account2", "deviant": deviant()})
        result = parse_account(test_config, [])
        self.assertEqual(result.deviant_config.gallery_ids, [])

    def test_allows_updating_config_based_on_rules_and_file_path(self):
        test_config = config(
            {
                "nsfw": False,
                "id": "test_account2",
                "deviant": deviant(
                    {
                        "tags": ["tag1", "tag2"],
                    }
                ),
            }
        )
        result = parse_account(test_config, [])
        result.set_config_for("./tests/fixtures/test/test.jpg")
        self.assertEqual(result.nsfw, True)
        self.assertEqual(result.deviant_config.featured, False)
        self.assertEqual(result.deviant_config.tags, ["tag1", "tag2", "testtag"])
        self.assertEqual(result.twitter_config.fixed_tags, ["#extra1", "#extra2"])
        self.assertEqual(result.deviant_config.default_mature_classification, "test")

    def test_cascades_multiple_configs_on_multiple_matches(self):
        deviant_config = deviant(
            {
                "gallery_ids": ["1"],
                "tags": ["tag1", "tag2"],
            }
        )
        test_config = config({"nsfw": False, "id": "test_account2", "deviant": deviant_config})
        result = parse_account(test_config, [])
        result.set_config_for("./tests/fixtures/test/other/test.jpg")
        self.assertEqual(result.nsfw, True)
        self.assertEqual(result.deviant_config.featured, True)
        self.assertEqual(result.deviant_config.default_mature_classification, "test")
        self.assertEqual(result.deviant_config.gallery_ids, ["1", "123"])
        self.assertEqual(result.deviant_config.tags, ["tag1", "tag2", "testtag", "othertesttag"])
        self.assertEqual(result.twitter_config.fixed_tags, ["#extra1", "#extra2", "#extra3"])
