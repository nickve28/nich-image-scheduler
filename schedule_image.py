import os
import glob
import random

import clients.deviant
import clients.twitter
from utils.cli_args import parse_arguments
from utils.constants import POSTED_TAG_MAPPING, QUEUE_TAG_MAPPING, TAG_MAPPING
from utils.image_metadata_adjuster import ImageMetadataAdjuster
from utils.account import select_account

args = parse_arguments()
account = args.account
account_data = select_account(account)

directory_path = account_data["directory_path"]
extensions = account_data["extensions"]
platforms = account_data["platforms"]

mode = args.mode

if mode is None or mode not in platforms:
    err = f"Please provide a valid mode. Choices are: {list(platforms)}"
    raise ValueError(err)

tag = TAG_MAPPING[mode]
queued_tag = QUEUE_TAG_MAPPING[mode]
posted_tag = POSTED_TAG_MAPPING[mode]


def find_random_image_in_folder(folder_path):
    image_paths = []

    for ext in extensions:
        file_with_ext = f"*{queued_tag}*{ext}"
        print(os.path.join(folder_path, file_with_ext))
        image_paths.extend(glob.glob(os.path.join(folder_path, file_with_ext)))
    return random.sample(image_paths, 1)[0]


def replace_file_tag(filepath):
    # Split the file path into directory, filename, and extension
    directory, basename = os.path.split(filepath)
    filename, file_extension = os.path.splitext(basename)

    # Construct the new filename
    new_name = filename.replace(queued_tag, posted_tag)
    new_filename = f"{new_name}{file_extension}"

    new_filepath = os.path.join(directory, new_filename)

    # Rename the file
    os.rename(filepath, new_filepath)
    print(f"Renamed {filepath} to {new_filepath}")
    return new_filepath


file = find_random_image_in_folder(directory_path)

caption = ImageMetadataAdjuster(file).get_caption()


def run():
    if mode == "Twitter":
        return clients.twitter.TwitterClient(account_data["twitter_config"]).schedule(file, caption)

    if mode == "Deviant":
        return clients.deviant.DeviantClient(account_data["deviant_config"]).schedule(file, caption)

    print(f"Mode {mode} not recognized")
    return False


if run() == True:
    new_filepath = replace_file_tag(file)

    # image adjuster currently hold a file reference which blocks editing the name
    adjuster = ImageMetadataAdjuster(new_filepath)
    adjuster.add_tags(tag)
    adjuster.save()
else:
    print(f"Upload failed. Halted on {file}")
