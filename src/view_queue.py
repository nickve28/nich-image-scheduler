import os
import glob

from utils.account_loader import select_account
from utils.cli_args import parse_arguments
from utils.constants import QUEUE_TAG_MAPPING

account_data = parse_arguments().account
account = select_account(account_data)

print(f"Checking queues for account {id}")
print("\n")

for platform in account.platforms:
    files = []
    print(f"Checking platform {platform}")

    platform_count = 0
    for extension in account.extensions:
        for directory_path in account.directory_paths:
            matches = glob.glob(os.path.join(directory_path, f"*{QUEUE_TAG_MAPPING[platform]}*{extension}"), recursive=True)
            platform_count += len(matches)
            for file_path in matches:
                print(file_path)
    print(f"Total of {platform_count} files queued for platform {platform}")
    print("\n")
