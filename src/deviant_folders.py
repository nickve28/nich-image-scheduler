import sys
from clients.deviant import DeviantClient
from utils.account_loader import select_account

from colorama import init, Fore

init(autoreset=True)  # Automatically resets colors back to normal after printing


def print_red(message):
    print(Fore.RED + message)


def print_green(message):
    print(Fore.GREEN + message)


if len(sys.argv) < 3:
    print_red("Please provide an id and deviant username.")
    sys.exit(1)

account_id = sys.argv[1]
account = select_account(account_id)

deviant_account_name = sys.argv[2]

print(f"Checking folders for account {deviant_account_name}")
print("\n")

client = DeviantClient(account)
response = client.list_folders(deviant_account_name)
for folder in response["results"]:
    print(f"{folder['name']}: {folder['folderid']}")
