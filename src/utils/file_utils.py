import fnmatch
import glob
import os
from typing import Dict, List

from models.account import Account
from utils.constants import DEVI_POSTED, QUEUE_TAG_MAPPING, POSTED_TAG_MAPPING, TWIT_POSTED


def replace_file_tag(filepath: str, old_tag: str, new_tag: str) -> str:
    # Replaces the old tag, eg: TWIT_Q with the new one, eg TWIT_P
    # Split the file path into directory, filename, and extension
    directory, basename = os.path.split(filepath)
    filename, file_extension = os.path.splitext(basename)

    # Construct the new filename
    new_name = filename.replace(old_tag, new_tag)
    new_filename = f"{new_name}{file_extension}"

    new_filepath = os.path.join(directory, new_filename)

    # Rename the file
    os.rename(filepath, new_filepath)
    print(f"Renamed {filepath} to {new_filepath}")
    rename_json_if_exists(filepath, new_filepath)
    return new_filepath


# Renames the given filepath, depending on the selected options provided in the platform_dict
# Adds or no-ops the platform_Q name, if selected
# Removes or no-ops the platform_Q name, if deselected
def rename_file_with_tags(filepath: str, platform_dict: Dict[str, bool]):
    # Split the file path into directory, filename, and extension
    directory, basename = os.path.split(filepath)
    filename, file_extension = os.path.splitext(basename)
    new_filename_without_extension = filename
    for platform, checked in platform_dict.items():
        # Check if tag is already in the filename
        queued_tag = QUEUE_TAG_MAPPING[platform]

        if (not checked) and queued_tag in filename:
            new_filename_without_extension = new_filename_without_extension.replace(queued_tag, "")
        elif checked and queued_tag not in filename:
            new_filename_without_extension = f"{new_filename_without_extension}{queued_tag}"
    new_filepath = os.path.join(directory, f"{new_filename_without_extension}{file_extension}")
    os.rename(filepath, new_filepath)
    print(f"Renamed {filepath} to {new_filepath}")
    rename_json_if_exists(filepath, new_filepath)
    return new_filepath


def rename_json_if_exists(filepath: str, new_filepath: str):
    # Check for corresponding JSON file and rename if it exists
    json_filepath = os.path.splitext(filepath)[0] + ".json"
    new_json_filepath = os.path.splitext(new_filepath)[0] + ".json"

    if os.path.exists(json_filepath):
        os.rename(json_filepath, new_json_filepath)
        print(f"Renamed {json_filepath} to {new_json_filepath}")
    else:
        print(f"No corresponding JSON file found for {filepath}")


def get_excluded_tags(account: Account, skip_posted: bool, skip_queued: bool):
    excluded_tags = []
    if skip_posted:
        excluded_tags.extend([POSTED_TAG_MAPPING[platform] for platform in account.platforms])
    if skip_queued:
        excluded_tags.extend([QUEUE_TAG_MAPPING[platform] for platform in account.platforms])
    return excluded_tags


def exclude_files(files: List[str], account: Account, skip_queued: bool, skip_posted=True):
    excluded_tags = get_excluded_tags(account, skip_posted, skip_queued)
    result = []
    for file in files:
        excluded_via_tags = any(tag in file for tag in excluded_tags)
        excluded_via_profile_path = False
        excluded_via_profile_exclusions = False

        for scheduler_profile in account.scheduler_profiles:
            if any(fnmatch.fnmatch(file, f"{exclude_path}/*") for exclude_path in scheduler_profile.exclude_paths):
                excluded_via_profile_exclusions = True

        if len(account.scheduler_profiles) > 0 and all(
            not fnmatch.fnmatch(file, f"{scheduler_profile.directory_path}/*") for scheduler_profile in account.scheduler_profiles
        ):
            excluded_via_profile_path = True

        if any([excluded_via_profile_exclusions, excluded_via_profile_path, excluded_via_tags]):
            continue
        result.append(file)

    return result


def find_images_in_folder(folder_path: str, account: Account, skip_queued: bool, skip_posted=True):
    image_paths = []
    for ext in account.extensions:
        files = glob.glob(os.path.join(folder_path, f"*{ext}"), recursive=True)
        filtered_files = exclude_files(files, account, skip_queued, skip_posted)
        image_paths.extend(filtered_files)
    return image_paths


def find_images_in_folders(account: Account, skip_queued: bool, skip_posted=True):
    result = []
    for folder_path in account.directory_paths:
        result += find_images_in_folder(folder_path, account, skip_queued, skip_posted)
    return result
