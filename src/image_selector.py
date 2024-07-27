import random
import os
import subprocess
import sys
from typing import Dict, List

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QCheckBox,
    QApplication,
    QLineEdit,
    QSizePolicy,
    QStatusBar,
)
from PyQt5.QtGui import QKeyEvent, QIcon, QPixmap, QPalette, QColor

from utils.cli_args import parse_arguments, get_scheduler_profile_ids
from utils.constants import DEVI_POSTED, DEVI_QUEUED, TWIT_POSTED, TWIT_QUEUED, POSTED_TAG_MAPPING, QUEUE_TAG_MAPPING
from utils.file_utils import find_images_in_folders, rename_file_with_tags
from utils.image_metadata_adjuster import ImageMetadataAdjuster
from utils.account_loader import select_account

args = parse_arguments()
account_data = args.account
scheduler_profile_ids = get_scheduler_profile_ids(args)
account = select_account(account_data, scheduler_profile_ids=scheduler_profile_ids)

sort = args.sort
limit = args.limit
skip_queued = args.skip_queued


class Scheduler(QMainWindow):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.setWindowTitle("Scheduler")

        # load the list of images and save it as full paths
        self._images: List[str] = find_images_in_folders(account, skip_queued=skip_queued)

        if len(self._images) == 0:
            err = f"No images found for account {account.id} using patterns {account.directory_paths}"
            raise RuntimeError(err)

        if sort == "random":
            random.shuffle(self._images)
        elif sort == "latest":
            self._images.sort(key=lambda x: os.path.getctime(x), reverse=True)
        else:
            self._images.sort()

        if limit is not None and limit < len(self._images):
            self._images = self._images[:limit]

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
        self._caption.setPlaceholderText("Enter a caption here...")

        # save
        self._submit_button = QPushButton("Save")
        self._submit_button.clicked.connect(self.submit_callback)

        # filepath display
        filepath_layout = QHBoxLayout()
        self._filepath_display = QLineEdit()
        self._filepath_display.setReadOnly(True)
        self._filepath_display.setPlaceholderText("File path will be displayed here")

        # Style the filepath display to look more obviously read-only
        palette = self._filepath_display.palette()
        palette.setColor(QPalette.Base, QColor(240, 240, 240))  # Light grey background
        palette.setColor(QPalette.Text, QColor(100, 100, 100))  # Darker grey text
        self._filepath_display.setPalette(palette)

        self._locate_button = QPushButton("locate")
        self._locate_button.clicked.connect(self.locate_file)
        self._locate_button.setToolTip("Locate file in explorer")

        filepath_layout.addWidget(self._filepath_display)
        filepath_layout.addWidget(self._locate_button)

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
        target_label = QLabel("Targets")
        target_label.setFixedHeight(20)
        target_layout.addWidget(target_label)

        # create checkboxes
        self._targets = account.platforms
        self._target_checkboxes: "list[QCheckBox]" = []
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
        central_layout.addLayout(filepath_layout)
        central_layout.addStretch()

        # create widget for the central layout
        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        # right layout
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)

        # Add a stretch at the top to push the content to the bottom
        right_layout.addStretch()

        right_layout.addWidget(target_widget, Qt.AlignTop)

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

        # Add status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

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
            button.clicked.connect(lambda checked, i=index: self.change_image(self._images[i], i))
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
        caption = ImageMetadataAdjuster(image).get_caption() or ""
        self._caption.setText(caption)

        # todo, can probably be done more elegant with mapping dicts
        posted_to_twitter = TWIT_POSTED in image
        queued_to_twitter = TWIT_QUEUED in image

        posted_to_deviant = DEVI_POSTED in image
        queued_to_deviant = DEVI_QUEUED in image

        for checkbox in self._target_checkboxes:
            if checkbox.text() == "Twitter":
                checkbox.setChecked((not posted_to_twitter) and queued_to_twitter)
                checkbox.setEnabled(not posted_to_twitter)

            if checkbox.text() == "Deviant":
                checkbox.setChecked((not posted_to_deviant) and queued_to_deviant)
                checkbox.setEnabled(not posted_to_deviant)

        # Update filepath display
        self._filepath_display.setText(image)

        # Update status bar with the current file name
        self._status_bar.showMessage(self.generate_summary())

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

        # Update filepath display with the new filename
        self._filepath_display.setText(new_filename)

        # Update status bar with the new file name
        self._status_bar.showMessage(self.generate_summary())

        self.update_image_selector_button(self._current_index, new_filename)

    def update_image_selector_button(self, index: int, new_filename: str) -> None:
        image_selector_widget = self._image_selector_area.widget()
        image_selector_layout = image_selector_widget.layout()
        button = image_selector_layout.itemAt(index).widget()
        button.setIcon(QIcon(new_filename))

    def locate_file(self):
        if not self._current_image:
            return

        file_path = os.path.abspath(self._current_image)
        if not os.path.exists(file_path):
            return

        if os.name == "nt":  # For Windows
            subprocess.run(["explorer", "/select,", file_path])
        elif os.name == "posix":  # For macOS and Linux
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", os.path.dirname(file_path)])

    def generate_summary(self):
        all_images = find_images_in_folders(account, False, False)
        total_images = len(all_images)
        summary = {"Twitter": {"posted": 0, "queued": 0, "rest": 0}, "Deviant": {"posted": 0, "queued": 0, "rest": 0}}

        for image in all_images:
            for platform in account.platforms:
                if POSTED_TAG_MAPPING[platform] in image:
                    summary[platform]["posted"] += 1
                elif QUEUE_TAG_MAPPING[platform] in image:
                    summary[platform]["queued"] += 1
                else:
                    summary[platform]["rest"] += 1

        summary_str = ""
        if len(account.directory_paths) > 1:
            summary_str += f"Multiple configured paths: {total_images} images"
        else:
            f"{account.directory_paths[0]}: {total_images} images."

        for platform in account.platforms:
            summary_str += (
                f" {platform}: posted: {summary[platform]['posted']}, queued: {summary[platform]['queued']}, rest: {summary[platform]['rest']}"
            )

        return summary_str


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Scheduler()
    sys.exit(app.exec_())
