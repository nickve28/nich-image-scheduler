import yaml
import os
import argparse
from deviant_utils.deviant_refresh_token import get_refresh_token

current_script_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_script_path, os.pardir))

def load_account_data(account_name):
    yaml_data = yaml.safe_load(open(os.path.join(parent_path, 'accounts.yml')))
    if account_name not in yaml_data:
        err = f"Account {account_name} not known in list. Should be one of: {list(yaml_data.keys())}"
        raise ValueError(err)

    account_data = yaml_data[account_name]

    # Set up account data
    data = {
        'ID': account_data['id'],
        'DIRECTORY_PATH': account_data['directory_path'],
        'EXTENSIONS': account_data['extensions'],
        'PLATFORMS': account_data['platforms'],
        'TWITTER_DATA': account_data.get('twitter', {}),
        'DEVIANT_DATA': account_data.get('deviant', {})
    }

    if 'deviant' in account_data:
        data['DEVIANT_DATA']['refresh_token'] = get_refresh_token(data['ID'])

    return data

def parse_arguments():
    parser = argparse.ArgumentParser(description="Image Selector and Scheduler")
    parser.add_argument('account', help="Account name matching the account(s) in the accounts.yml file")
    parser.add_argument('mode', nargs='?', choices=['Twitter', 'Deviant'], help="Platform to schedule the image for (only for schedule_image.py)")
    return parser.parse_args()

args = parse_arguments()

account_data = load_account_data(args.account)
