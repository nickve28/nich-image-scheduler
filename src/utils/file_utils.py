import glob
import os
from typing import Dict

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


def exclude_files(files, platforms):
    excluded_tags = [POSTED_TAG_MAPPING[platform] for platform in platforms]
    return [f for f in files if not any(tag in f for tag in excluded_tags)]


def find_images_in_folder(folder_path, extensions, platforms):
    image_paths = []
    for ext in extensions:
        files = glob.glob(os.path.join(folder_path, f"*{ext}"))
        filtered_files = exclude_files(files, platforms)
        image_paths.extend(filtered_files)
    return image_paths
