import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from string_utils import capitalize_words


class TestCapitalizeWords(unittest.TestCase):
    def test_basic(self):
        """capitalize_words('hello world') must return 'Hello World'"""
        self.assertEqual(capitalize_words("hello world"), "Hello World")

    def test_empty(self):
        self.assertEqual(capitalize_words(""), "")

    def test_already_capitalized(self):
        self.assertEqual(capitalize_words("Hello World"), "Hello World")


if __name__ == "__main__":
    unittest.main()
