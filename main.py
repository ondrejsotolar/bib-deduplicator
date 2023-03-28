import os
import sys
from pathlib import Path
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from typing import Dict


def search_dir(pth, recursive):
    """
    Search directory for files with .bib suffix.
    :param pth: start search here
    :param recursive: search all subdirectories
    :return: list of .bib file paths
    """
    bibfiles = []
    l = os.walk(str(pth), topdown=True, onerror=None, followlinks=False)
    for (dirpath, dirnames, filenames) in l:
        for f in filenames:
            if f.endswith(".bib"):
                bibfiles.append(str(Path(dirpath, f)))
    return bibfiles


def read_records(pth: Path, throw_if_invalid: bool) -> BibDatabase:
    """
    Retrieve citation record key and the whole record from .bib file.
    :param pth: .bib file
    :param throw_if_invalid: throws ValueError on parse error otherwise tries to parse further
    :return: dict where keys are the record keys and values the whole records
    """
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False
    parser.homogenise_fields = False

    with open(pth) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, parser)
    return bib_database


def merge_records(records: Dict[str, dict], duplicates: Dict[str, dict], new_records: BibDatabase) -> None:
    """
    Borrows records and duplicates and merges them with new_records to have distinct keys in records.
    :param records: records with distinct keys
    :param duplicates: records with keys that were already in records
    :param duplicates: new records
    :return: None
    """
    for n in new_records.entries:
        if n["ID"] in records:
            i = 0
            suffix = "_" + str(i)
            while n["ID"] + suffix in duplicates:
                i += 1
                suffix = "_" + str(i)
            duplicates[n["ID"] + suffix] = n
        else:
            records[n["ID"]] = n


def write_records(records: Dict[str, dict], output_name):
    new_bd: BibDatabase = BibDatabase()
    new_bd.entries = records.values()
    f = open(output_name, "w")
    bibtexparser.dump(new_bd, f)
    f.close()


def run(pth: Path, output_name: str, recursive: bool, throw_if_invalid: bool) -> None:
    bibs = search_dir(pth, recursive)

    records = {}
    duplicates = {}

    for p in bibs:
        recs = read_records(Path(p), throw_if_invalid)
        merge_records(records, duplicates, recs)
    write_records(records, output_name)
    write_records(duplicates, output_name.split(".")[0] + "_duplicates." + output_name.split(".")[1])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Specify at least: root directory, output name")
        sys.exit()

    if not os.path.exists(sys.argv[0]):
        print("invalid root directory")
        sys.exit()

    if len(sys.argv) == 2:
        run(Path(sys.argv[0]), sys.argv[1], recursive=False, throw_if_invalid=True)
    else:
        print("TODO")
        sys.exit()


