import os
import glob

from utils.account import select_account
from utils.cli_args import parse_arguments
from utils.constants import QUEUE_TAG_MAPPING

account = parse_arguments().account
account_data = select_account(account)

# Use the account data based on the provided account name
id = account_data["id"]
directory_path = account_data["directory_path"]
extensions = account_data["extensions"]
platforms = account_data["platforms"]

print(f"Checking queues for account {id}")
print("\n")

for platform in platforms:
    files = []
    print(f"Checking platform {platform}")

    platform_count = 0
    for extension in extensions:
        matches = glob.glob(os.path.join(directory_path, f"*{QUEUE_TAG_MAPPING[platform]}*{extension}"))
        platform_count += len(matches)
        for file_path in matches:
            print(file_path)
    print(f"Total of {platform_count} files queued for platform {platform}")
    print("\n")
