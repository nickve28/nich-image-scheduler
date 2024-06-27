from typing import List, Optional
from enum import Enum

from deviant_utils.deviant_refresh_token import get_refresh_token


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
    tag_count: int
    tags: List[str]

    DEFAULT_TAGS = [
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
        self.tag_count = config.get("tag_count", 2)
        self.tags = config.get("tags", self.DEFAULT_TAGS)


class DeviantPlatformConfig(PlatformConfig):
    client_id: str
    client_secret: str
    default_mature_classification: str
    refresh_token: str

    def __init__(self, id, config):
        self.id = id
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.default_mature_classification = config.get("mature_classification", "")
        self.refresh_token = get_refresh_token(id)


PLATFORM_CLASS_BY_NAME = {SupportedPlatforms.DEVIANT: DeviantPlatformConfig, SupportedPlatforms.TWITTER: TwitterPlatformConfig}


class Account:
    """Representation of the loaded account configuration"""

    id: str
    directory_path: str
    extensions: List[str]
    platforms: List[str]
    nsfw: bool
    twitter_config: Optional[TwitterPlatformConfig]
    deviant_config: Optional[DeviantPlatformConfig]

    def __init__(self, account_config):
        self.id = account_config["id"]
        self.directory_path = account_config["directory_path"]
        self.extensions = account_config["extensions"]
        self.platforms = account_config["platforms"]
        self.nsfw = account_config.get("nsfw", False)

        if SupportedPlatforms.DEVIANT.value in account_config:
            self.deviant_config = DeviantPlatformConfig(self.id, account_config[SupportedPlatforms.DEVIANT.value])

        if SupportedPlatforms.TWITTER.value in account_config:
            self.twitter_config = TwitterPlatformConfig(self.id, account_config[SupportedPlatforms.TWITTER.value])
