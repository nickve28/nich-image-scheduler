import glob
import os
import random
import sys
from typing import Dict

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QCheckBox,
    QMessageBox, QApplication, QLineEdit, QSizePolicy
)
from PyQt5.QtGui import QKeyEvent, QIcon, QPixmap

from image_metadata_adjuster import ImageMetadataAdjuster

DIRECTORY_PATH = os.getenv('DIRECTORY_PATH')
EXTENSIONS = os.getenv('EXTENSIONS').split(',')
MODE = os.getenv('MODE')
PLATFORMS = os.getenv('PLATFORMS', '').split(',')

TWIT_POSTED = 'TWIT_P'
TWIT_QUEUED = 'TWIT_Q'

DEVI_POSTED = 'DEVI_P'
DEVI_QUEUED = 'DEVI_Q'

QUEUE_TAG_MAPPING = {
    'Twitter': TWIT_QUEUED,
    'Deviant': DEVI_QUEUED
}

POSTED_TAG_MAPPING = {
    'Twitter': TWIT_POSTED,
    'Deviant': DEVI_POSTED
}

def rename_file_with_tags(filepath: str, platform_dict: Dict[str, bool]):
    # Split the file path into directory, filename, and extension
    directory, basename = os.path.split(filepath)
    filename, file_extension = os.path.splitext(basename)
    new_filename_without_extension = filename
    for platform, checked in platform_dict.items():
        # Check if tag is already in the filename
        queued_tag = QUEUE_TAG_MAPPING[platform]
        print(checked, queued_tag, filename)
        if (not checked) and queued_tag in filename:
            new_filename_without_extension = new_filename_without_extension.replace(queued_tag, '')
        elif checked and queued_tag not in filename:
            new_filename_without_extension = f"{filename}{queued_tag}"
    new_filepath = os.path.join(directory, f"{new_filename_without_extension}{file_extension}")
    print(f"Renaming {filepath} to {new_filepath}")
    os.rename(filepath, new_filepath)
    return new_filepath

def exclude_files(files):
    return [f for f in files if (TWIT_POSTED not in f) and (DEVI_POSTED not in f)]

def find_images_in_folder(folder_path):
    image_paths = []
    for ext in EXTENSIONS:
        print(os.path.join(folder_path, f'*{ext}'))
        files = glob.glob(os.path.join(folder_path, f'*{ext}'))
        filtered_files = exclude_files(files)
        filtered_files = files
        image_paths.extend(filtered_files)
    random.shuffle(image_paths)
    return image_paths

class Scheduler(QMainWindow):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.setWindowTitle("Scheduler")

        # load the list of images and save it as full paths
        self._images: 'list[str]' = find_images_in_folder(DIRECTORY_PATH)

        # sort them
        self._images.sort()

        # prepare the window
        self.setup_window()

        # show window
        self.show()

        # set the first image by default
        self.change_image(self._images[0], 0)

    def keyPressEvent(self, e: QKeyEvent) -> None:  # type: ignore
        if e.key() == Qt.Key_Escape:
            self.close()
            return

    def setup_window(self) -> None:
        # current image
        self._image = QLabel()

        # current caption
        self._caption = QLineEdit()
        self._caption.setPlaceholderText('Enter a caption here...')

        # save
        self._submit_button = QPushButton('Save')
        self._submit_button.clicked.connect(self.submit_callback)

        # image selector
        self._image_selector_area = QScrollArea()
        self._image_selector_area.setWidgetResizable(True)
        self._image_selector_area.setFocusPolicy(Qt.NoFocus)
        self._image_selector_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._image_selector_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._image_selector_area.setFixedHeight(1000)
        self._image_selector_area.setFixedWidth(220)

        pose_selector_content_layout = QVBoxLayout()
        pose_selector_content_layout.setContentsMargins(10, 10, 20, 10)
        pose_selector_content_layout.addStretch()

        # populate the image selector
        self.populate_image_selector()

        # target layout
        target_layout = QVBoxLayout()
        target_layout.setContentsMargins(0, 0, 0, 0)

        # create label
        target_label = QLabel('Targets')
        target_label.setFixedHeight(20)
        target_layout.addWidget(target_label)

        # create checkboxes
        self._targets = PLATFORMS
        self._target_checkboxes: 'list[QCheckBox]' = []
        for target in self._targets:
            checkbox = QCheckBox(target)
            checkbox.setFixedHeight(20)
            target_layout.addWidget(checkbox)
            self._target_checkboxes.append(checkbox)

        target_layout.addStretch()

        # create widget for the target layout
        target_widget = QWidget()
        target_widget.setLayout(target_layout)
        target_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # central layout
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(10, 10, 10, 10)
        central_layout.addStretch()
        central_layout.addWidget(self._image)
        central_layout.addWidget(self._caption)
        central_layout.addWidget(self._submit_button)
        central_layout.addStretch()

        # create widget for the central layout
        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        # right layout
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.addSpacing(20)
        right_layout.addWidget(target_widget, Qt.AlignTop)
        right_layout.addStretch()

        # create widget for the right layout
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addStretch()
        main_layout.addWidget(self._image_selector_area)
        main_layout.addWidget(central_widget)
        main_layout.addWidget(right_widget)
        main_layout.addStretch()

        # set the window layout
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def populate_image_selector(self) -> None:
        # create a layout for the image selector
        image_selector_layout = QVBoxLayout()
        image_selector_layout.setContentsMargins(10, 10, 20, 10)

        # create a button for each image
        for index, image in enumerate(self._images):
            button = QPushButton()
            button.setIcon(QIcon(image))
            button.setIconSize(QSize(200, 200))
            button.setFixedSize(200, 200)
            button.clicked.connect(lambda checked, image=image: self.change_image(image, index))
            image_selector_layout.addWidget(button)

        image_selector_layout.addStretch()

        # set the layout
        image_selector_widget = QWidget()
        image_selector_widget.setLayout(image_selector_layout)

        # set the widget to the scroll area
        self._image_selector_area.setWidget(image_selector_widget)

    def change_image(self, image: str, index: int) -> None:
        self._current_image = image
        self._current_index = index

        # change the image
        self._image.setPixmap(QPixmap(image).scaledToHeight(900, Qt.SmoothTransformation))

        # change the caption
        caption = ImageMetadataAdjuster(image).get_caption() or 'Enter caption here...'
        self._caption.setText(caption)

        # todo, can probably be done more elegant with mapping dicts
        posted_to_twitter = TWIT_POSTED in image
        queued_to_twitter = TWIT_QUEUED in image

        posted_to_deviant = DEVI_POSTED in image
        queued_to_deviant = DEVI_QUEUED in image

        for checkbox in self._target_checkboxes:
            if checkbox.text() == 'Twitter':
              checkbox.setChecked((not posted_to_twitter) and queued_to_twitter)
              checkbox.setEnabled(not posted_to_twitter)

            if checkbox.text() == 'Deviant':
              checkbox.setChecked((not posted_to_deviant) and queued_to_deviant)
              checkbox.setEnabled(not posted_to_deviant)

    def submit_callback(self) -> None:
        caption = self._caption.text()
        adjuster = ImageMetadataAdjuster(self._current_image) 
        adjuster.add_subject(caption)
        adjuster.save()
        platforms = dict([[checkbox.text(), checkbox.isChecked()] for checkbox in self._target_checkboxes])
        new_filename = rename_file_with_tags(self._current_image, platforms)

        # Make sure the name is updated for subsequent saves
        self._current_image = new_filename
        self._images[self._current_index] = new_filename 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Scheduler()
    sys.exit(app.exec_())
