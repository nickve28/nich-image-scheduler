import argparse


def parse_arguments():
    # Reads the provided CLI arguments for further use in the app
    parser = argparse.ArgumentParser(description="Image Selector and Scheduler")
    parser.add_argument("account", help="Account name matching the account(s) in the accounts.yml file")
    parser.add_argument(
        "mode", nargs="?", choices=["Twitter", "Deviant", "Debug"], help="Platform to schedule the image for (only for schedule_image.py)"
    )
    parser.add_argument(
        "--sort", choices=["random", "latest", "alphabetical"], default="alphabetical", help="Sorting method for images (default: random)"
    )
    parser.add_argument("--limit", type=int, help="Limit the number of images to process")
    parser.add_argument("--skip-queued", action="store_true", help="Skip already queued images")
    return parser.parse_args()
