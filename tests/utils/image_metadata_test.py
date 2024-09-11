import unittest
import os
from PIL import Image
import piexif
from utils.image_metadata_adjuster import ImageMetadataAdjuster


def create_test_image(path):
    img = Image.new("RGB", (100, 100), color="red")
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    exif_bytes = piexif.dump(exif_dict)
    img.save(path, exif=exif_bytes)


class TestImageMetadataAdjuster(unittest.TestCase):
    def setUp(self):
        self.test_image_path = "test.jpg"
        create_test_image(self.test_image_path)

    def tearDown(self):
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)

    def test_set_and_get_content_tags(self):
        adjuster = ImageMetadataAdjuster(self.test_image_path)

        # Test setting initial tags
        adjuster.set_content_tags("tag1, tag2, tag3")
        adjuster.save()
        self.assertEqual(adjuster.get_content_tags(), "tag1, tag2, tag3")

        # Test replacing tags
        adjuster.set_content_tags("tag4, tag5")
        adjuster.save()
        self.assertEqual(adjuster.get_content_tags(), "tag4, tag5")

        # Test setting with duplicate tags
        adjuster.set_content_tags("tag1, tag1, tag2")
        adjuster.save()
        self.assertEqual(adjuster.get_content_tags(), "tag1, tag2")

    def test_tag_limit(self):
        adjuster = ImageMetadataAdjuster(self.test_image_path)

        # Create a long string of tags that exceeds the limit
        long_tags = ", ".join([f"tag{i}" for i in range(300)])

        # Test that setting too many tags raises an exception
        with self.assertRaises(ValueError):
            adjuster.set_content_tags(long_tags)

    def test_no_existing_tags(self):
        adjuster = ImageMetadataAdjuster(self.test_image_path)
        self.assertEqual(adjuster.get_content_tags(), "")

    def test_clear_all_tags(self):
        adjuster = ImageMetadataAdjuster(self.test_image_path)

        # Set initial tags
        adjuster.set_content_tags("tag1, tag2, tag3")
        adjuster.save()

        # Clear all tags by setting an empty string
        adjuster.set_content_tags("")
        adjuster.save()

        self.assertEqual(adjuster.get_content_tags(), "")

    def test_tag_with_spaces(self):
        adjuster = ImageMetadataAdjuster(self.test_image_path)

        # Set tags with spaces, expecting spaces to be replaced with underscores
        adjuster.set_content_tags("tag with space, another tag")
        adjuster.save()

        self.assertEqual(adjuster.get_content_tags(), "another_tag, tag_with_space")

    def test_tag_with_special_characters(self):
        adjuster = ImageMetadataAdjuster(self.test_image_path)

        # Set tags with special characters, expecting them to be replaced with underscores
        adjuster.set_content_tags("tag1!, tag@2, tag#3$")
        adjuster.save()

        self.assertEqual(adjuster.get_content_tags(), "tag1_, tag_2, tag_3_")

    def test_combined_case(self):
        adjuster = ImageMetadataAdjuster(self.test_image_path)

        # Set tags with both spaces and special characters
        adjuster.set_content_tags("hello world!, invalid*chars here")
        adjuster.save()

        self.assertEqual(adjuster.get_content_tags(), "hello_world_, invalid_chars_here")
