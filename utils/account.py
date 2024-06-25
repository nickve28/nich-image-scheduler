import yaml
import os
from deviant_utils.deviant_refresh_token import get_refresh_token

current_script_path = os.path.dirname(
    os.path.abspath(__file__)
)
parent_path = os.path.abspath(os.path.join(current_script_path, os.pardir))

ACCOUNT = os.getenv('ACCOUNT')
if ACCOUNT is None:
    raise RuntimeError("Please provide an ACCOUNT= environment var matching the account(s) in the accounts.yml file")

yaml_data = yaml.safe_load(open(os.path.join(parent_path, 'accounts.yml')))
if ACCOUNT not in yaml_data:
    err = f"Account {ACCOUNT} not known in list. Should be one of: {list(yaml_data.keys())}"
    raise RuntimeError(err)

account_data = yaml_data[ACCOUNT]

# exports
ID = account_data['id']
DIRECTORY_PATH = account_data['directory_path']
EXTENSIONS = account_data['extensions']
PLATFORMS = account_data['platforms']
TWITTER_DATA = account_data['twitter'] if 'twitter' in account_data else {}
DEVIANT_DATA = account_data['deviant'] if 'deviant' in account_data else {}

if 'deviant' in account_data:
    DEVIANT_DATA['refresh_token'] = get_refresh_token(ID)
