import unittest
from pathlib import Path

from main import run


class MyTestCase(unittest.TestCase):
    def test_something(self):
        run(Path("testdata"), Path("testdata", "testoutput.bib"))


if __name__ == '__main__':
    unittest.main()
