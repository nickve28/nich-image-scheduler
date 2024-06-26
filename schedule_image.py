import os
import glob
import random

import clients.deviant
import clients.twitter
from utils.image_metadata_adjuster import ImageMetadataAdjuster
from utils.account import account_data, args

DIRECTORY_PATH = account_data['DIRECTORY_PATH']
EXTENSIONS = account_data['EXTENSIONS']
PLATFORMS = account_data['PLATFORMS']

mode = args.mode

if mode is None or mode not in PLATFORMS:
    err = f"Please provide a valid mode. Choices are: {list(PLATFORMS)}"
    raise ValueError(err)

tag_mapping = {
    'Twitter': 'TWIT',
    'Deviant': 'DEVI'
}

tag = tag_mapping[mode]
queued_tag = f'_{tag}_Q'
posted_tag = f'_{tag}_P'

def find_random_image_in_folder(folder_path):
    image_paths = []

    for ext in EXTENSIONS:
        file_with_ext = f'*{queued_tag}*{ext}'
        print(os.path.join(folder_path, file_with_ext))
        image_paths.extend(glob.glob(os.path.join(folder_path, file_with_ext)))
    return random.sample(image_paths, 1)[0]

def replace_file_tag(filepath):
    # Split the file path into directory, filename, and extension
    directory, basename = os.path.split(filepath)
    filename, file_extension = os.path.splitext(basename)

    # Construct the new filename
    new_name = filename.replace(queued_tag, posted_tag)
    new_filename = f'{new_name}{file_extension}'

    new_filepath = os.path.join(directory, new_filename)

    # Rename the file
    os.rename(filepath, new_filepath)
    print(f"Renamed {filepath} to {new_filepath}")
    return new_filepath

file = find_random_image_in_folder(DIRECTORY_PATH)

caption = ImageMetadataAdjuster(file).get_caption()

def run():
    if mode == 'Twitter':
        return clients.twitter.schedule(file, caption)

    if mode == 'Deviant':
        return clients.deviant.schedule(file, caption)

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
