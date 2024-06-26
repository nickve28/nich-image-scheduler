import yaml
import os
from deviant_utils.deviant_refresh_token import get_refresh_token

current_script_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_script_path, os.pardir))


def load_accounts():
    # Loads the provided accounts.yml file to use
    return yaml.safe_load(open(os.path.join(parent_path, "accounts.yml")))


def select_account(account_name: str):
    # Selects a single account, fails if the account name can not be found
    accounts = load_accounts()

    if account_name not in accounts:
        err = f"Account {account_name} not known in list. Should be one of: {list(accounts.keys())}"
        raise ValueError(err)

    account_data = accounts[account_name]

    # Set up account data
    data = {
        "ID": account_data["id"],
        "DIRECTORY_PATH": account_data["directory_path"],
        "EXTENSIONS": account_data["extensions"],
        "PLATFORMS": account_data["platforms"],
        "TWITTER_DATA": account_data.get("twitter", {}),
        "DEVIANT_DATA": account_data.get("deviant", {}),
    }

    if "deviant" in account_data:
        data["DEVIANT_DATA"]["refresh_token"] = get_refresh_token(data["ID"])

    return data
