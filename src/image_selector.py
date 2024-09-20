import random
import os
import subprocess
import sys
from typing import Dict, List

from PyQt5.QtCore import Qt, QSize, QTimer
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
    QShortcut,
)
from PyQt5.QtGui import QKeyEvent, QIcon, QPixmap, QPalette, QColor, QKeySequence

from clients.deviant import DeviantClient
from clients.twitter import TwitterClient
from utils.cli_args import parse_arguments, get_scheduler_profile_ids
from utils.constants import DEVI_POSTED, DEVI_QUEUED, TWIT_POSTED, TWIT_QUEUED, POSTED_TAG_MAPPING, QUEUE_TAG_MAPPING
from utils.file_utils import find_images_in_folders, rename_file_with_tags, replace_file_tag
from utils.image_metadata_adjuster import ImageMetadataAdjuster
from utils.account_loader import select_account

args = parse_arguments()
account_data = args.account
scheduler_profile_ids = get_scheduler_profile_ids(args)
account = select_account(account_data, scheduler_profile_ids=scheduler_profile_ids)

sort = args.sort
limit = args.limit
skip_queued = args.skip_queued


def post_now(filename, mode):
    account_copy = select_account(account_data, scheduler_profile_ids=scheduler_profile_ids)
    account_copy.set_config_for(filename)
    caption = ImageMetadataAdjuster(filename).get_caption() or ""
    content_tags = ImageMetadataAdjuster(filename).get_content_tags() or ""

    response = False
    if mode == "Twitter":
        response = TwitterClient(account_copy).schedule(filename, caption)

    if mode == "Deviant":
        response = DeviantClient(account_copy).schedule(filename, caption, content_tags)

    if response is not False:
        queue_tag = QUEUE_TAG_MAPPING[mode]
        post_tag = POSTED_TAG_MAPPING[mode]
        new_filepath = replace_file_tag(filename, queue_tag, post_tag)

        # image adjuster currently hold a file reference which blocks editing the name
        adjuster = ImageMetadataAdjuster(new_filepath)
        adjuster.add_tags(mode)
        adjuster.save()
        return new_filepath
    return False


class Scheduler(QMainWindow):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.setWindowTitle("Scheduler")

        self.setMinimumSize(1000, 700)

        # load the list of images and save it as full paths
        self._images: List[str] = find_images_in_folders(account, account.platforms, skip_queued=skip_queued)

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

        # Timer to control resize after the resize event ends
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.resize_image)

        # prepare the window
        self.setup_window()

        # show window
        self.show()

        # set the first image by default
        self.change_image(self._images[0], 0)

        self.setup_shortcuts()

    def setup_shortcuts(self):
        # Shortcut for toggling Deviant checkbox
        self.toggle_deviant_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.toggle_deviant_shortcut.activated.connect(self.toggle_deviant_checkbox)

        # Shortcut for toggling Twitter checkbox
        self.toggle_twitter_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.toggle_twitter_shortcut.activated.connect(self.toggle_twitter_checkbox)

        # Shortcut for saving (pressing the save button)
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.submit_callback)

        # Shortcut for navigating to previous image
        self.prev_image_shortcut = QShortcut(QKeySequence("F1"), self)
        self.prev_image_shortcut.activated.connect(self.show_previous_image)

        # Shortcut for navigating to next image
        self.next_image_shortcut = QShortcut(QKeySequence("F2"), self)
        self.next_image_shortcut.activated.connect(self.show_next_image)

    def toggle_deviant_checkbox(self):
        self.toggle_platform_checkbox("Deviant")

    def toggle_twitter_checkbox(self):
        self.toggle_platform_checkbox("Twitter")

    def toggle_platform_checkbox(self, platform):
        checkbox = next((checkbox for checkbox in self._target_checkboxes if checkbox.text() == platform), None)
        if checkbox and checkbox.isEnabled():
            checkbox.setChecked(not checkbox.isChecked())
            # self.submit_callback()  # Automatically save the changes

    def show_previous_image(self):
        if self._current_index > 0:
            self.change_image(self._images[self._current_index - 1], self._current_index - 1)

    def show_next_image(self):
        if self._current_index < len(self._images) - 1:
            self.change_image(self._images[self._current_index + 1], self._current_index + 1)

    def keyPressEvent(self, e: QKeyEvent) -> None:  # type: ignore
        if e.key() == Qt.Key_Escape:
            self.close()
            return
        super().keyPressEvent(e)  # Call the parent class method to handle other key events

    def setup_window(self) -> None:
        # current image
        self._image = QLabel()
        self._image.setAlignment(Qt.AlignCenter)
        self._image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # current caption
        self._caption = QLineEdit()
        self._caption.setPlaceholderText("Enter a caption here...")

        # tags
        self._content_tags = QLineEdit()
        self._content_tags.setPlaceholderText("Enter comma separated tags here...")

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
        self._image_selector_area.setFixedWidth(220)
        self._image_selector_area.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        pose_selector_content_layout = QVBoxLayout()
        pose_selector_content_layout.setContentsMargins(10, 10, 20, 10)
        pose_selector_content_layout.addStretch()

        # populate the image selector
        self.populate_image_selector()

        # target layout
        target_layout = QVBoxLayout()
        target_layout.setContentsMargins(0, 0, 0, 0)

        target_layout.addStretch()

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

        def post_image_now(target):
            new_filename = post_now(self._current_image, target)

            if new_filename is False:
                raise RuntimeError("Error during saving")
            # Make sure the name is updated for subsequent saves
            self._current_image = new_filename
            self._images[self._current_index] = new_filename

            # Update filepath display with the new filename
            self._filepath_display.setText(new_filename)

            # Update status bar with the new file name
            self._status_bar.showMessage(self.generate_summary())

            self.update_image_selector_button(self._current_index, new_filename)

        # add instant post buttons
        for index, target in enumerate(self._targets):
            button = QPushButton(f"Post now ({target})")
            # todo
            # post_tag = POSTED_TAG_MAPPING[target]
            # button.setDisabled(post_tag in self._current_image)
            button.clicked.connect(lambda state, index=index: post_image_now(self._targets[index]))  #
            target_layout.addWidget(button)

        # create widget for the target layout
        target_widget = QWidget()
        target_widget.setLayout(target_layout)
        target_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # central layout
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(10, 10, 10, 10)
        central_layout.addWidget(self._image, 1)
        central_layout.addWidget(self._caption)
        central_layout.addWidget(self._content_tags)
        central_layout.addWidget(self._submit_button)
        central_layout.addLayout(filepath_layout)

        # create widget for the central layout
        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # right layout
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
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
        main_layout.addWidget(central_widget, 1)
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

        # Resize the image when changed
        self.resize_image()

        # change the caption
        caption = ImageMetadataAdjuster(image).get_caption() or ""
        self._caption.setText(caption)

        # change the tags
        content_tags = ImageMetadataAdjuster(image).get_content_tags() or ""
        self._content_tags.setText(content_tags)

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

        # Set focus on the caption input
        self._caption.setFocus()
        # Move cursor to the end of the text
        self._caption.setCursorPosition(len(caption))

    def resize_image(self):
        pixmap = QPixmap(self._current_image)

        # Get the size of the image label
        label_size = self._image.size()

        # Calculate the scaling factor to fit the image within the label
        scale_factor = min(label_size.width() / pixmap.width(), label_size.height() / pixmap.height(), 1)

        # Calculate the new size
        new_size = QSize(int(pixmap.width() * scale_factor), int(pixmap.height() * scale_factor))

        # Scale the pixmap and set it to the label
        scaled_pixmap = pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._image.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Handle the window resize event."""
        if hasattr(self, "_current_image"):
            # Start or restart the timer every time the window is resized
            self.resize_timer.start(300)  # 300ms delay after resizing ends

    def submit_callback(self) -> None:
        caption = self._caption.text()
        content_tags = self._content_tags.text()
        adjuster = ImageMetadataAdjuster(self._current_image)
        adjuster.add_subject(caption)
        adjuster.set_content_tags(content_tags)
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
        all_images = find_images_in_folders(account, account.platforms, False, False)
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
