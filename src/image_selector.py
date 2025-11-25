import argparse
import random
import os
import subprocess
import sys
from typing import List

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
    QTabWidget,
    QMessageBox,
)
from PyQt5.QtGui import QKeyEvent, QIcon, QPixmap, QPalette, QColor, QKeySequence

from clients.deviant import DeviantClient
from clients.twitter import TwitterClient
from utils.constants import DEVI_POSTED, DEVI_QUEUED, TWIT_POSTED, TWIT_QUEUED, POSTED_TAG_MAPPING, QUEUE_TAG_MAPPING
from utils.file_utils import find_images_in_folders, rename_file_with_tags, replace_file_tag
from utils.image_metadata_adjuster import ImageMetadataAdjuster
from utils.account_loader import load_accounts, parse_account
from models.account import Account


def post_now(filename: str, mode: str, account: Account) -> str | bool:
    """Post an image immediately to the specified platform"""
    account.set_config_for(filename)
    caption = ImageMetadataAdjuster(filename).get_caption() or ""
    content_tags = ImageMetadataAdjuster(filename).get_content_tags() or ""

    response = False
    if mode == "Twitter":
        response = TwitterClient(account).schedule(filename, caption)

    if mode == "Deviant":
        response = DeviantClient(account).schedule(filename, caption, content_tags)

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


class SchedulerWidget(QWidget):
    """Individual scheduler widget for one account (formerly the main Scheduler class)"""
    def __init__(self, account, main_window=None, sort="alphabetical", limit: int | None =None, skip_queued=False):
        super(SchedulerWidget, self).__init__()

        self.account: Account = account
        self.main_window = main_window

        # load the list of images and save it as full paths
        self._images: List[str] = find_images_in_folders(account, account.platforms, skip_queued=skip_queued)

        if len(self._images) == 0:
            # Don't raise error, just show empty message
            self._images = []

        if sort == "random":
            random.shuffle(self._images)
        elif sort == "latest":
            self._images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        else:
            self._images.sort()

        if limit is not None and limit < len(self._images):
            self._images = self._images[:limit]

        # Timer to control resize after the resize event ends
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.resize_image)

        # prepare the widget
        self.setup_widget()

        # set the first image by default if we have images
        if self._images:
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

    def toggle_platform_checkbox(self, platform: str):
        checkbox = next((checkbox for checkbox in self._target_checkboxes if checkbox.text() == platform), None)
        if checkbox and checkbox.isEnabled():
            checkbox.setChecked(not checkbox.isChecked())

    def show_previous_image(self):
        if self._current_index > 0:
            self.change_image(self._images[self._current_index - 1], self._current_index - 1)

    def show_next_image(self):
        if self._current_index < len(self._images) - 1:
            self.change_image(self._images[self._current_index + 1], self._current_index + 1)

    def setup_widget(self) -> None:
        if not self._images:
            # Show message for no images
            no_images_label = QLabel(f"No images found for account '{self.account.id}'\nPaths: {self.account.directory_paths}")
            no_images_label.setAlignment(Qt.AlignCenter)
            layout = QVBoxLayout()
            layout.addWidget(no_images_label)
            self.setLayout(layout)
            return

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
        self._targets: List[str] = self.account.platforms
        self._target_checkboxes: "list[QCheckBox]" = []
        for target in self._targets:
            checkbox = QCheckBox(target)
            checkbox.setFixedHeight(20)
            target_layout.addWidget(checkbox)
            self._target_checkboxes.append(checkbox)

        def post_image_now(target: str) -> None:
            new_filename = post_now(self._current_image, target, self.account)

            if new_filename is False:
                QMessageBox.warning(self, "Error", f"Failed to post to {target}")
                return

            # Make sure the name is updated for subsequent saves
            self._current_image = new_filename
            self._images[self._current_index] = new_filename

            # Update filepath display with the new filename
            self._filepath_display.setText(new_filename)

            self.update_image_selector_button(self._current_index, new_filename)

            # Update status bar to reflect new counts
            if self.main_window:
                self.main_window.update_status_bar(self.main_window.tab_widget.currentIndex())

        # add instant post buttons
        for index, target in enumerate(self._targets):
            button = QPushButton(f"Post now ({target})")
            button.clicked.connect(lambda state, index=index: post_image_now(self._targets[index]))
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

        # set the widget layout
        self.setLayout(main_layout)

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

        # Set focus on the caption input
        self._caption.setFocus()
        # Move cursor to the end of the text
        self._caption.setCursorPosition(len(caption))

    def resize_image(self):
        if not hasattr(self, '_current_image'):
            return

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
        """Handle the widget resize event."""
        if hasattr(self, "_current_image"):
            # Start or restart the timer every time the widget is resized
            self.resize_timer.start(300)  # 300ms delay after resizing ends

    def submit_callback(self) -> None:
        if not hasattr(self, '_current_image'):
            return

        caption = self._caption.text()
        content_tags = self._content_tags.text()
        adjuster = ImageMetadataAdjuster(self._current_image)
        adjuster.add_subject(caption)
        adjuster.set_content_tags(content_tags)
        adjuster.save()
        platforms = dict([[checkbox.text(), checkbox.isChecked()] for checkbox in self._target_checkboxes])
        new_filename = rename_file_with_tags(self._current_image, platforms, caption)

        # Make sure the name is updated for subsequent saves
        self._current_image = new_filename
        self._images[self._current_index] = new_filename

        # Update filepath display with the new filename
        self._filepath_display.setText(new_filename)

        self.update_image_selector_button(self._current_index, new_filename)

        # Update status bar to reflect new counts
        if self.main_window:
            self.main_window.update_status_bar(self.main_window.tab_widget.currentIndex())

    def update_image_selector_button(self, index: int, new_filename: str) -> None:
        image_selector_widget = self._image_selector_area.widget()
        image_selector_layout = image_selector_widget.layout()
        button = image_selector_layout.itemAt(index).widget()
        button.setIcon(QIcon(new_filename))

    def locate_file(self):
        if not hasattr(self, '_current_image') or not self._current_image:
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


class TabbedSchedulerWindow(QMainWindow):
    """Main window containing tabs for each account"""
    def __init__(self, sort: str = "alphabetical", limit: int | None = None, skip_queued: bool = False):
        super(TabbedSchedulerWindow, self).__init__()
        self.setWindowTitle("Image Scheduler")
        self.setMinimumSize(1200, 800)

        try:
            accounts_data = load_accounts()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load accounts.yml: {e}")
            sys.exit(1)

        if not accounts_data:
            QMessageBox.warning(self, "Warning", "No accounts found in accounts.yml")
            sys.exit(1)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create a tab for each account
        for account_name, account_config in accounts_data.items():
            try:
                account = parse_account(account_config, scheduler_profile_ids=[])
                scheduler_widget = SchedulerWidget(account=account, main_window=self, sort=sort, limit=limit, skip_queued=skip_queued)
                self.tab_widget.addTab(scheduler_widget, account_name)
            except Exception as e:
                error_widget = QLabel(f"Error loading account '{account_name}':\n{str(e)}")
                error_widget.setAlignment(Qt.AlignCenter)
                self.tab_widget.addTab(error_widget, f"{account_name} (Error)")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Update status bar based on current tab
        self.tab_widget.currentChanged.connect(self.update_status_bar)
        self.update_status_bar(0)

    def update_status_bar(self, index: int):
        """Update status bar based on the current tab"""
        current_widget = self.tab_widget.widget(index)
        if isinstance(current_widget, SchedulerWidget) and hasattr(current_widget, 'account'):
            account = current_widget.account
            all_images = find_images_in_folders(account, account.platforms, False, False)
            total_images = len(all_images)

            # Count posted images (contain any _P tag)
            posted_tags = [POSTED_TAG_MAPPING[platform] for platform in account.platforms]
            posted_images = [img for img in all_images if any(tag in img for tag in posted_tags)]
            posted_count = len(posted_images)

            # Count queued images (contain any _Q tag)
            queued_tags = [QUEUE_TAG_MAPPING[platform] for platform in account.platforms]
            queued_images = [img for img in all_images if any(tag in img for tag in queued_tags)]
            queued_count = len(queued_images)

            # Count remaining images (neither posted nor queued)
            remaining_count = total_images - posted_count - queued_count

            self.status_bar.showMessage(f"Account: {account.id} | Total: {total_images} | Posted: {posted_count} | Queued: {queued_count} | Remaining: {remaining_count}")
        else:
            self.status_bar.showMessage("Ready")

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_Escape:
            self.close()
            return
        super().keyPressEvent(e)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Image Scheduler")
    parser.add_argument("--sort", choices=["random", "latest", "alphabetical"], default="alphabetical", help="Sorting method for images (default: alphabetical)")
    parser.add_argument("--limit", type=int, help="Limit the number of images to process")
    parser.add_argument("--skip-queued", action="store_true", help="Skip already queued images")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    app = QApplication(sys.argv)
    window = TabbedSchedulerWindow(sort=args.sort, limit=args.limit, skip_queued=args.skip_queued)
    window.show()
    sys.exit(app.exec_())
