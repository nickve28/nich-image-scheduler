import yaml
import os
from models.account import Account

current_script_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_script_path, os.pardir))

project_root = os.path.abspath(os.path.join(parent_path, ".."))


def parse_account(account_data):
    # Set up account data
    # This function shouldn't be used directly, but rather is exported for testing
    return Account(account_data)


def load_accounts(file_path=project_root):
    # Loads the provided accounts.yml file to use
    return yaml.safe_load(open(os.path.join(file_path, "accounts.yml")))


def select_account(account_name: str, file_path=project_root):
    # Selects a single account, fails if the account name can not be found
    accounts = load_accounts(file_path)

    if account_name not in accounts:
        err = f"Account {account_name} not known in list. Should be one of: {list(accounts.keys())}"
        raise ValueError(err)

    return parse_account(accounts[account_name])
