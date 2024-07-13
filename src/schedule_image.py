import os
import glob
import random

import clients.deviant
import clients.twitter
import clients.test
from utils.cli_args import parse_arguments
from utils.constants import POSTED_TAG_MAPPING, QUEUE_TAG_MAPPING, TAG_MAPPING
from utils.file_utils import replace_file_tag
from utils.image_metadata_adjuster import ImageMetadataAdjuster
from utils.account_loader import select_account

args = parse_arguments()
account_data = args.account
account = select_account(account_data)

mode = args.mode
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


def find_random_image_in_folder(folder_path):
    image_paths: "list[str]" = []

    for ext in account.extensions:
        file_with_ext = f"*{queued_tag}*{ext}"
        print(os.path.join(folder_path, file_with_ext))
        image_paths.extend(glob.glob(os.path.join(folder_path, file_with_ext), recursive=True))
    if len(image_paths) == 0:
        return None
    return random.sample(image_paths, 1)[0]


file = find_random_image_in_folder(account.directory_path)

if file is None:
    err = f"No file found for glob: {account.directory_path} and extensions {', '.join(account.extensions)}"
    raise ValueError(err)

caption = ImageMetadataAdjuster(file).get_caption()


def run():
    if mode == "Twitter":
        return clients.twitter.TwitterClient(account).schedule(file, caption)

    if mode == "Deviant":
        return clients.deviant.DeviantClient(account).schedule(file, caption)

    if mode == "Debug":
        return clients.test.TestClient(account).schedule(file, caption)

    print(f"Mode {mode} not recognized")
    return False


if run() == True:
    new_filepath = replace_file_tag(file, queued_tag, posted_tag)

    # image adjuster currently hold a file reference which blocks editing the name
    adjuster = ImageMetadataAdjuster(new_filepath)
    adjuster.add_tags(tag)
    adjuster.save()
else:
    print(f"Upload failed. Halted on {file}")
