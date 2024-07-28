from typing import Dict
import unittest
from models.account import Account
from factories.factories import account, config, scheduler_profile
from utils.account_loader import load_accounts, select_account, parse_account
from utils.file_utils import exclude_files


def get_paths():
    return [
        "/pictures/folder1/to-post/image1.jpg",
        "/pictures/folder1/nested/to-post/image2.jpg",
        "/pictures/folder1/to-post/image3_TWIT_Q.jpg",
        "/pictures/folder2/to-post/image4_TWIT_P.jpg",
        "/pictures/folder1/to-post/image5_DEVI_P.jpg",
        "/pictures/folder1/nested/to-post/image6_TWIT_Q.jpg",
        "/pictures/folder1/nested/to-post/image7_TWIT_P.jpg",
        "/pictures/folder2/to-post/nested/image8_DEVI_P.jpg",
    ]


class TestFileUtils(unittest.TestCase):

    def test_no_ops_without_specific_filters(self):
        acc = account()
        self.assertListEqual(exclude_files(get_paths(), acc, skip_posted=False, skip_queued=False), get_paths())

    def test_skips_queued_images_when_specified(self):
        acc = account()
        self.assertListEqual(
            exclude_files(get_paths(), acc, skip_posted=False, skip_queued=True),
            [
                "/pictures/folder1/to-post/image1.jpg",
                "/pictures/folder1/nested/to-post/image2.jpg",
                "/pictures/folder2/to-post/image4_TWIT_P.jpg",
                "/pictures/folder1/to-post/image5_DEVI_P.jpg",
                "/pictures/folder1/nested/to-post/image7_TWIT_P.jpg",
                "/pictures/folder2/to-post/nested/image8_DEVI_P.jpg",
            ],
        )

    def test_skips_posted_images_when_specified(self):
        acc = account()
        self.assertListEqual(
            exclude_files(get_paths(), acc, skip_posted=True, skip_queued=False),
            [
                "/pictures/folder1/to-post/image1.jpg",
                "/pictures/folder1/nested/to-post/image2.jpg",
                "/pictures/folder1/to-post/image3_TWIT_Q.jpg",
                "/pictures/folder1/nested/to-post/image6_TWIT_Q.jpg",
            ],
        )

    def test_skips_both_posted_and_queued_when_both_specified(self):
        acc = account()
        self.assertListEqual(
            exclude_files(get_paths(), acc, skip_posted=True, skip_queued=True),
            [
                "/pictures/folder1/to-post/image1.jpg",
                "/pictures/folder1/nested/to-post/image2.jpg",
            ],
        )

    def test_skips_entries_excluded_via_selected_scheduler_profiles(self):
        acc = account(config({"scheduler_profiles": {"regular": scheduler_profile()}}), ["regular"])
        self.assertListEqual(
            exclude_files(get_paths(), acc, skip_posted=False, skip_queued=False),
            [
                "/pictures/folder1/to-post/image1.jpg",
                "/pictures/folder1/to-post/image3_TWIT_Q.jpg",
                "/pictures/folder2/to-post/image4_TWIT_P.jpg",
                "/pictures/folder1/to-post/image5_DEVI_P.jpg",
                "/pictures/folder2/to-post/nested/image8_DEVI_P.jpg",
            ],
        )

    def test_scheduler_profiles_no_ops_without_selection(self):
        acc = account(config({"scheduler_profiles": {"regular": scheduler_profile()}}), [])
        self.assertListEqual(
            exclude_files(get_paths(), acc, skip_posted=False, skip_queued=False),
            get_paths(),
        )

    def test_skips_entries_excluded_via_scheduler_profile_path(self):
        acc = account(config({"scheduler_profiles": {"regular": scheduler_profile({"directory_path": "**/folder2/*post*"})}}), ["regular"])
        self.assertListEqual(
            exclude_files(get_paths(), acc, skip_posted=False, skip_queued=False),
            [
                "/pictures/folder2/to-post/image4_TWIT_P.jpg",
                "/pictures/folder2/to-post/nested/image8_DEVI_P.jpg",
            ],
        )
