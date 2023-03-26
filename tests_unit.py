import unittest
from pathlib import Path

from main import run


class MyTestCase(unittest.TestCase):
    def test_something(self):
        run(Path("testdata"), "testoutput.bib", recursive=False, throw_if_invalid=False)


if __name__ == '__main__':
    unittest.main()
