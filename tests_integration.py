import os
import unittest
from pathlib import Path

from main import run


def rminsidedir(directory, prefix: str):
    directory = Path(directory)
    with os.scandir(directory) as d:
        for item in d:
            item = Path(item)
            if item.name.startswith(prefix):
                item.unlink()


class MyTestCase(unittest.TestCase):
    def test_file_content_match_1(self):
        actual_pth = Path("testresults", "actual1.bib")
        actual_duplicates_pth = Path("testresults", "actual1_duplicates.bib")
        expected_pth = Path("testresults", "expected1.bib")
        expected_duplicates_pth = Path("testresults", "expected1_duplicates.bib")

        run(Path("testdata"), actual_pth)

        actual = actual_pth.read_text()
        actual_duplicates = actual_duplicates_pth.read_text()
        expected = expected_pth.read_text()
        expected_duplicates = expected_duplicates_pth.read_text()

        assert actual == expected
        assert actual_duplicates == expected_duplicates

        rminsidedir("testresults", "actual")


if __name__ == '__main__':
    unittest.main()
