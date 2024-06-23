import os
import glob
import random
import sys
import tkinter as tk
from PIL import Image, ImageTk

import clients.deviant
import clients.twitter
from image_metadata_adjuster import ImageMetadataAdjuster

directory_path = os.getenv('DIRECTORY_PATH')
extensions = os.getenv('EXTENSIONS').split(',')
mode = os.getenv('MODE')

tag_mapping = {
    'Twitter': 'TWIT',
    'Deviant': 'DEVI'
}

tag = tag_mapping[mode]
queued_tag = f'_{tag}_Q_'
posted_tag = f'_{tag}_P_'

def find_random_image_in_folder(folder_path):
    image_paths = []
    
    for ext in extensions:
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

file = find_random_image_in_folder(directory_path)

caption = ImageMetadataAdjuster(file).get_caption()

if mode == 'Twitter':
    clients.twitter.schedule(file, "", caption)

if mode == 'Deviant':
    clients.deviant.schedule(file, "", caption)

replace_file_tag(file)