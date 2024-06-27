import yaml
import os
from deviant_utils.deviant_refresh_token import get_refresh_token

current_script_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_script_path, os.pardir))

project_root = os.path.abspath(os.path.join(parent_path, ".."))


def load_accounts(file_path=project_root):
    # Loads the provided accounts.yml file to use
    return yaml.safe_load(open(os.path.join(file_path, "accounts.yml")))


def select_account(account_name: str, file_path=project_root):
    # Selects a single account, fails if the account name can not be found
    accounts = load_accounts(file_path)

    if account_name not in accounts:
        err = f"Account {account_name} not known in list. Should be one of: {list(accounts.keys())}"
        raise ValueError(err)

    account_data = accounts[account_name]

    # Set up account data
    data = {
        "id": account_data["id"],
        "directory_path": account_data["directory_path"],
        "extensions": account_data["extensions"],
        "platforms": account_data["platforms"],
        "nsfw": account_data.get("nsfw", False),
        "twitter_config": account_data.get("twitter", {}),
        "deviant_config": account_data.get("deviant", {}),
    }

    if "deviant" in account_data:
        data["deviant_config"]["refresh_token"] = get_refresh_token(data["id"])

    return data
