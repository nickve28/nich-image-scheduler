import os
import glob

from utils.account import account_data, args

# Use the account data based on the provided account name
ID = account_data['ID']
DIRECTORY_PATH = account_data['DIRECTORY_PATH']
EXTENSIONS = account_data['EXTENSIONS']
PLATFORMS = account_data['PLATFORMS']

print(f"Checking queues for account {ID}")
print("\n")

QUEUE_MAP = {
    "Twitter": "TWIT_Q",
    "Deviant": "DEVI_Q"
}

for platform in PLATFORMS:
    files = []
    print(f"Checking platform {platform}")

    platform_count = 0
    for extension in EXTENSIONS:
        matches = glob.glob(os.path.join(DIRECTORY_PATH, f'*{QUEUE_MAP[platform]}*{extension}'))
        platform_count += len(matches)
        for file_path in matches:
            print(file_path)
    print(f"Total of {platform_count} files queued for platform {platform}")
    print("\n")