import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from calculator import divide, accumulate, normalize


class TestDivide(unittest.TestCase):
    def test_normal(self):
        """divide(10, 2) must return 5.0"""
        self.assertEqual(divide(10, 2), 5.0)


class TestAccumulate(unittest.TestCase):
    def test_sum(self):
        """accumulate([1, 2, 3]) must return 6"""
        self.assertEqual(accumulate([1, 2, 3]), 6)


class TestNormalize(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(normalize([1, 2, 3]), [0.0, 0.5, 1.0])

    def test_empty(self):
        self.assertEqual(normalize([]), [])


if __name__ == "__main__":
    unittest.main()
