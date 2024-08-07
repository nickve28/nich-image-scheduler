import unittest
from factories.factories import account, config, scheduler_profile
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
        self.assertListEqual(exclude_files(get_paths(), acc, []), get_paths())

    def test_skips_queued_images_when_specified(self):
        acc = account()
        self.assertListEqual(
            exclude_files(get_paths(), acc, ["TWIT_Q", "DEVI_Q"]),
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
            exclude_files(get_paths(), acc, ["TWIT_P", "DEVI_P"]),
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
            exclude_files(get_paths(), acc, ["TWIT_Q", "DEVI_Q", "TWIT_P", "DEVI_P"]),
            [
                "/pictures/folder1/to-post/image1.jpg",
                "/pictures/folder1/nested/to-post/image2.jpg",
            ],
        )

    def test_skips_entries_excluded_via_selected_scheduler_profiles(self):
        acc = account(config({"scheduler_profiles": {"regular": scheduler_profile()}}), ["regular"])
        self.assertListEqual(
            exclude_files(get_paths(), acc, []),
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
            exclude_files(get_paths(), acc, []),
            get_paths(),
        )

    def test_skips_entries_excluded_via_scheduler_profile_path(self):
        acc = account(config({"scheduler_profiles": {"regular": scheduler_profile({"directory_path": "**/folder2/*post*"})}}), ["regular"])
        self.assertListEqual(
            exclude_files(get_paths(), acc, []),
            [
                "/pictures/folder2/to-post/image4_TWIT_P.jpg",
                "/pictures/folder2/to-post/nested/image8_DEVI_P.jpg",
            ],
        )
