from typing import Dict
import unittest
from utils.text_utils import remove_duplicates

class TestTextUtils(unittest.TestCase):
    def test_removes_duplicates_successfully(self):
        result = remove_duplicates(['a', 'b', 'c', 'c', 'c', 'b'])
        self.assertEqual(result, ['a', 'b', 'c'])
