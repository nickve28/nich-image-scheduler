import fnmatch
import glob
import itertools
import os
import re
from typing import Dict, List, Optional

from models.account import Account
from utils.constants import QUEUE_TAG_MAPPING, POSTED_TAG_MAPPING


def sanitize_caption_for_filename(caption: str, max_length: int = 100) -> str:
    """Sanitize a caption for use in a filename.

    Removes invalid characters and limits length.
    """
    if not caption:
        return ""

    # Remove or replace invalid filename characters
    # Keep only alphanumeric, spaces, hyphens, underscores, and basic punctuation
    sanitized = re.sub(r'[<>:"/\\|?*]', '', caption)
    sanitized = re.sub(r'[\n\r\t]', ' ', sanitized)  # Replace newlines/tabs with spaces
    sanitized = re.sub(r'\s+', ' ', sanitized)  # Collapse multiple spaces
    sanitized = sanitized.strip()

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()

    return sanitized


def add_caption_to_filename(filename: str, caption: str) -> str:
    """Add or update a caption in a filename using _[caption] format.

    Args:
        filename: Filename without extension (e.g., 'image_DEVI_Q')
        caption: Caption to add

    Returns:
        Filename with caption added/updated
    """
    sanitized_caption = sanitize_caption_for_filename(caption)
    if not sanitized_caption:
        # If no caption, remove any existing caption
        return re.sub(r'_\[.*?\]', '', filename)

    # Check if there's already a caption in brackets
    if re.search(r'_\[.*?\]', filename):
        # Replace existing caption
        return re.sub(r'_\[.*?\]', f'_[{sanitized_caption}]', filename)
    else:
        # Add new caption - insert before any platform tags
        # Find the position of the first platform tag
        tag_pattern = r'(_DEVI_[QP]|_TWIT_[QP])'
        match = re.search(tag_pattern, filename)
        if match:
            # Insert caption before the tag
            pos = match.start()
            return filename[:pos] + f'_[{sanitized_caption}]' + filename[pos:]
        else:
            # No tags found, just append
            return f'{filename}_[{sanitized_caption}]'


def replace_file_tag(filepath: str, old_tag: str, new_tag: str) -> str:
    # Replaces the old tag, eg: TWIT_Q with the new one, eg TWIT_P
    # Split the file path into directory, filename, and extension
    directory, basename = os.path.split(filepath)
    filename, file_extension = os.path.splitext(basename)

    # Construct the new filename
    new_name = None
    if old_tag in filename:
        new_name = filename.replace(old_tag, new_tag)
    else:
        new_name = f"{filename}{new_tag}"
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
def rename_file_with_tags(filepath: str, platform_dict: Dict[str, bool], caption: str = ""):
    # Split the file path into directory, filename, and extension
    directory, basename = os.path.split(filepath)
    filename, file_extension = os.path.splitext(basename)
    new_filename_without_extension = filename

    # Add or update caption first
    new_filename_without_extension = add_caption_to_filename(new_filename_without_extension, caption)

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


def get_excluded_tags(platforms: List[str], skip_posted: bool, skip_queued: bool) -> List[str]:
    # Get tags which will be excluded from the results
    excluded_tags = []
    if skip_posted:
        excluded_tags.extend([POSTED_TAG_MAPPING[platform] for platform in platforms])
    if skip_queued:
        excluded_tags.extend([QUEUE_TAG_MAPPING[platform] for platform in platforms])
    return excluded_tags


def matches_path(file, pattern):
    return fnmatch.fnmatch(file, f"{pattern}/*")


def is_included_via_scheduler_profile_paths(account: Account, file: str):
    # If one directory path of the scheduler profile matches, include the item
    for scheduler_profile in account.scheduler_profiles:
        if matches_path(file, scheduler_profile.directory_path):
            return True
    return False


def is_excluded_via_scheduler_profile_exclusions(account: Account, file: str):
    # If one exclude path of the scheduler profile matches, exclude the item
    for scheduler_profile in account.scheduler_profiles:
        for exclude_path in scheduler_profile.exclude_paths:
            if matches_path(file, exclude_path):
                return True
    return False


def is_excluded_file(account: Account, file: str, excluded_tags: List[str]):
    is_excluded_via_tags = any(tag in file for tag in excluded_tags)

    if is_excluded_via_tags:
        return True

    # No-op without scheduler profiles
    if len(account.scheduler_profiles) == 0:
        return False

    if is_excluded_via_scheduler_profile_exclusions(account, file):
        return True

    return not is_included_via_scheduler_profile_paths(account, file)


def exclude_files(files: List[str], account: Account, excluded_tags: List[str]):
    return [file for file in files if not is_excluded_file(account, file, excluded_tags)]


def find_images_in_folder(folder_path: str, account: Account, excluded_tags: List[str]):
    image_paths = []
    for ext in account.extensions:
        files = glob.glob(os.path.join(folder_path, f"*{ext}"), recursive=True)
        files = [os.path.abspath(file) for file in files]
        filtered_files = exclude_files(files, account, excluded_tags)
        image_paths.extend(filtered_files)
    return image_paths


def find_images_in_folders(account: Account, platforms: List[str], skip_queued: bool, skip_posted: bool=True):
    excluded_tags = get_excluded_tags(platforms, skip_posted, skip_queued)
    result = []
    for folder_path in account.directory_paths:
        result += find_images_in_folder(folder_path, account, excluded_tags)
    return result
