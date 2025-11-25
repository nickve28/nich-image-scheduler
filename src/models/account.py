import fnmatch
from typing import Dict, List, Optional
from enum import Enum

from deviant_utils.deviant_refresh_token import get_refresh_token


def get_directory_paths(config):
    if "directory_paths" in config:
        return config["directory_paths"]
    return {"primary": config["directory_path"]}


class SupportedPlatforms(Enum):
    TWITTER = "twitter"
    DEVIANT = "deviant"


class PlatformConfig:
    def __init__(self, id, config):
        pass


class TwitterPlatformConfig(PlatformConfig):
    consumer_key: str
    consumer_secret: str
    bearer_token: str
    access_token: str
    access_token_secret: str
    client_id: str
    client_secret: str
    cursive_font: bool
    tag_position: str
    random_tag_count: int
    random_tags: List[str]
    fixed_tags: List[str]

    DEFAULT_RANDOM_TAGS = [
        "#AIart",
        "#AIイラスト",
        "#AIArtwork",
        "#AIArtCommunity",
        "#AIArtGallery",
        "#AIArtworks",
        "#AIgirls",
    ]

    def __init__(self, id, config):
        self.id = id
        self.consumer_key = config["consumer_key"]
        self.consumer_secret = config["consumer_secret"]
        self.bearer_token = config["bearer_token"]
        self.access_token = config["access_token"]
        self.access_token_secret = config["access_token_secret"]
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.cursive_font = config.get("cursive_font", False)
        self.tag_position = config.get("tag_position", "append")
        self.random_tag_count = config.get("random_tag_count", 2)
        self.random_tags = config.get("random_tags", self.DEFAULT_RANDOM_TAGS)
        self.fixed_tags = config.get("fixed_tags", [])


class DeviantPlatformConfig(PlatformConfig):
    client_id: str
    client_secret: str
    default_mature_classification: str
    refresh_token: str
    featured: bool
    gallery_ids: List[str]
    premium_gallery_ids: List[str]
    tags: List[str]

    def __init__(self, id, config):
        self.id = id
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.default_mature_classification = config.get("mature_classification", "")
        self.refresh_token = get_refresh_token(id)
        self.featured = config.get("featured", True)
        self.gallery_ids = config.get("gallery_ids", [])
        self.premium_gallery_ids = config.get("premium_gallery_ids", [])
        self.tags = config.get("tags", [])


PLATFORM_CLASS_BY_NAME = {SupportedPlatforms.DEVIANT: DeviantPlatformConfig, SupportedPlatforms.TWITTER: TwitterPlatformConfig}


def matches_path(config: Dict[str, any], path: str) -> bool:
    pattern = f"{config['directory_path']}/*"
    return fnmatch.fnmatch(path, pattern)


class SchedulerProfile:
    def __init__(self, id, profile_config):
        self.id = id
        self.directory_path = profile_config["directory_path"]
        self.exclude_paths = profile_config.get("exclude_paths", [])


class Account:
    """Representation of the loaded account configuration"""

    id: str
    scheduler_profiles: List[SchedulerProfile]
    # the named directory paths will become more relevant when scheduler profiles are implemented
    named_directory_paths: Dict[str, str]
    directory_paths: List[str]
    extensions: List[str]
    platforms: List[str]
    nsfw: bool
    twitter_config: Optional[TwitterPlatformConfig]
    deviant_config: Optional[DeviantPlatformConfig]
    _config: Dict[str, any]

    def __init__(self, account_config, scheduler_profile_ids=[]):
        self.id = account_config["id"]
        self.named_directory_paths = get_directory_paths(account_config)
        self.directory_paths = list(self.named_directory_paths.values())
        self.extensions = account_config["extensions"]
        self.platforms = account_config["platforms"]
        self.nsfw = account_config.get("nsfw", False)
        self._config = account_config
        self.scheduler_profiles = [
            SchedulerProfile(scheduler_profile_id, account_config["scheduler_profiles"][scheduler_profile_id])
            for scheduler_profile_id in scheduler_profile_ids
        ]

        self.deviant_config = None
        self.twitter_config = None

        if SupportedPlatforms.DEVIANT.value in account_config:
            self.deviant_config = DeviantPlatformConfig(self.id, account_config[SupportedPlatforms.DEVIANT.value])

        if SupportedPlatforms.TWITTER.value in account_config:
            self.twitter_config = TwitterPlatformConfig(self.id, account_config[SupportedPlatforms.TWITTER.value])

    def set_config_for(self, path: str):
        """
        Merges sub configs and creates an account configuration based on the given file path
        This allows for generating specific configuration for folders, like adding specific tags
        """

        matching_sub_configs = [sub_config for sub_config in self._config.get("sub_configs", []) if matches_path(sub_config, path)]
        for sub_config in matching_sub_configs:
            self.nsfw = sub_config.get("nsfw", self.nsfw)

            if self.deviant_config and "deviant" in sub_config:
                self._update_deviant_config(sub_config["deviant"])

            if self.twitter_config and "twitter" in sub_config:
                self._update_twitter_config(sub_config["twitter"])

    def _update_deviant_config(self, deviant_sub_config: Dict[str, any]):
        self.deviant_config.premium_gallery_ids += deviant_sub_config.get("additional_premium_gallery_ids", [])
        self.deviant_config.gallery_ids += deviant_sub_config.get("additional_gallery_ids", [])
        self.deviant_config.tags += deviant_sub_config.get("additional_tags", [])
        self.deviant_config.default_mature_classification = deviant_sub_config.get(
            "default_mature_classification", self.deviant_config.default_mature_classification
        )
        self.deviant_config.featured = deviant_sub_config.get("featured", self.deviant_config.featured)

    def _update_twitter_config(self, twitter_sub_config: Dict[str, any]):
        self.twitter_config.fixed_tags += twitter_sub_config.get("additional_fixed_tags", [])
