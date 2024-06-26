import glob
import os
from typing import Dict

from utils.constants import DEVI_POSTED, QUEUE_TAG_MAPPING, TWIT_POSTED


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
    print(f"Renaming {filepath} to {new_filepath}")
    os.rename(filepath, new_filepath)
    return new_filepath


def exclude_files(files):
    # todo only filter active platforms
    return [f for f in files if (TWIT_POSTED not in f) and (DEVI_POSTED not in f)]


# Based on the provided glob path, and whitelisted extensions
# Find the files matching said pattern
def find_images_in_folder(folder_path, extensions):
    image_paths = []
    for ext in extensions:
        files = glob.glob(os.path.join(folder_path, f"*{ext}"))
        filtered_files = exclude_files(files)
        image_paths.extend(filtered_files)
    return image_paths
