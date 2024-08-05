import os
import glob
import random
from typing import List

import clients.deviant
import clients.twitter
import clients.test
from models.account import Account
from utils.cli_args import parse_arguments, get_scheduler_profile_ids
from utils.constants import POSTED_TAG_MAPPING, QUEUE_TAG_MAPPING, TAG_MAPPING
from utils.file_utils import replace_file_tag, find_images_in_folders
from utils.image_metadata_adjuster import ImageMetadataAdjuster
from utils.account_loader import select_account


def execute(account: Account, mode: str):
    debugging = mode == "Debug"

    if ((mode is None) or (mode not in account.platforms)) and (not debugging):
        err = f"Please provide a valid mode. Choices are: {list(account.platforms)}"
        raise ValueError(err)

    def read_from(dict, key, fallback):
        if debugging:
            return fallback
        return dict[key]

    tag = read_from(TAG_MAPPING, mode, "TWIT")
    queued_tag = read_from(QUEUE_TAG_MAPPING, mode, "TWIT_Q")
    posted_tag = read_from(POSTED_TAG_MAPPING, mode, "TWIT_P")

    files = find_images_in_folders(account, [mode], skip_queued=False, skip_posted=True)
    files = [file for file in files if queued_tag in file]

    if len(files) == 0:
        err = f"No file found for glob: {account.directory_paths} and extensions {', '.join(account.extensions)}"
        raise ValueError(err)

    file = random.sample(files, 1)[0]
    caption = ImageMetadataAdjuster(file).get_caption()

    def run():
        account.set_config_for(file)
        if mode == "Twitter":
            return clients.twitter.TwitterClient(account).schedule(file, caption)

        if mode == "Deviant":
            return clients.deviant.DeviantClient(account).schedule(file, caption)

        if mode == "Debug":
            return clients.test.TestClient(account).schedule(file, caption)

        print(f"Mode {mode} not recognized")
        return False

    result = run()
    if result is not False:
        new_filepath = replace_file_tag(file, queued_tag, posted_tag)

        # image adjuster currently hold a file reference which blocks editing the name
        adjuster = ImageMetadataAdjuster(new_filepath)
        adjuster.add_tags(tag)
        adjuster.save()
    else:
        print(f"Upload failed. Halted on {file}")

    return result


if __name__ == "__main__":
    args = parse_arguments()
    account_data = args.account
    scheduler_profile_ids = get_scheduler_profile_ids(args)
    account = select_account(account_data, scheduler_profile_ids=scheduler_profile_ids)
    execute(account, args.mode)
