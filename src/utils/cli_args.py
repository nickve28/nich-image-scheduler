import argparse


def parse_arguments():
    # Reads the provided CLI arguments for further use in the app
    parser = argparse.ArgumentParser(description="Image Selector and Scheduler")
    parser.add_argument("account", help="Account name matching the account(s) in the accounts.yml file")
    parser.add_argument("mode", nargs="?", choices=["Twitter", "Deviant"], help="Platform to schedule the image for (only for schedule_image.py)")
    return parser.parse_args()
