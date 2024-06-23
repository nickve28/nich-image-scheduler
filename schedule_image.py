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

tag = f'_{tag_mapping[mode]}_'

def find_random_image_in_folder(folder_path):
    image_paths = []
    
    for ext in extensions:
        file_with_ext = f'*{tag}*{ext}'
        print(os.path.join(folder_path, file_with_ext))
        image_paths.extend(glob.glob(os.path.join(folder_path, file_with_ext)))
    return random.sample(image_paths, 1)[0]

file = find_random_image_in_folder(directory_path)

adjuster = ImageMetadataAdjuster(file)
caption = adjuster.get_caption()

if mode == 'Twitter':
    clients.twitter.schedule(file, "", caption)

if mode == 'Deviant':
    clients.deviant.schedule(file, "", caption)