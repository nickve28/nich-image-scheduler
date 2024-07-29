from typing import Dict
from models.account import Account


def deep_merge(dict1, dict2):
    merged = dict1.copy()

    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value

    return merged


def twitter(partial: Dict[str, any] = {}):
    return deep_merge(
        {
            "consumer_key": "t123",
            "consumer_secret": "t456",
            "bearer_token": "AAAAAAAAAAAAAAAAAAAAA",
            "access_token": "t111",
            "access_token_secret": "t222",
            "client_id": "t21",
            "client_secret": "t22",
            "cursive_font": True,
            "tag_position": "prepend",
            "random_tag_count": 2,
            "random_tags": ["#AIart", "#AIArtwork", "#AIArtCommunity", "#AIArtGallery", "#AIArtworks"],
        },
        partial,
    )


def deviant(partial: Dict[str, any] = {}):
    return deep_merge(
        {
            "client_id": 123,
            "client_secret": 456,
            "default_mature_classification": "",
            "refresh_token": None,
            "featured": True,
        },
        partial,
    )


def sub_config(partial: Dict[str, any] = {}):
    return deep_merge(
        {
            "directory_path": "./tests/fixtures/test",
            "nsfw": True,
            "deviant": {"default_mature_classification": "test", "featured": False, "additional_tags": ["testtag"]},
            "twitter": {"additional_fixed_tags": ["#extra1", "#extra2"]},
        },
        partial,
    )


def scheduler_profile(partial: Dict[str, any] = {}):
    return deep_merge({"directory_path": "**/*post*", "exclude_paths": ["**/nested/*post*"]}, partial)


def config(partial: Dict[str, any] = {}):
    return deep_merge(
        {
            "id": "my_account",
            "directory_path": "./tests/fixtures",
            "extensions": ["jpg", "jpeg"],
            "platforms": ["Twitter", "Deviant"],
            "nsfw": False,
            "twitter": twitter(),
            "deviant": deviant(),
            "sub_configs": [
                sub_config(),
                sub_config(
                    {
                        "directory_path": "./tests/fixtures/**/other",
                        "deviant": {
                            "additional_gallery_ids": ["123"],
                            "featured": True,
                            "additional_tags": ["othertesttag"],
                        },
                        "twitter": {"additional_fixed_tags": ["#extra3"]},
                    }
                ),
            ],
            "scheduler_profiles": {},
        },
        partial,
    )


def account(account_config: Dict[str, any] = {}, scheduler_profile_ids=[]):
    return Account(config(account_config), scheduler_profile_ids)
