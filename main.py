import os
import sys
from pathlib import Path
import bibtexparser as pp
from bibtexparser.bibdatabase import BibDatabase, UndefinedString
from bibtexparser.bparser import BibTexParser
from typing import Dict


def search_dir(pth):
    """
    Search directory for files with .bib suffix.
    :param pth: start search here
    :return: list of .bib file paths
    """
    bibfiles = []
    l = os.walk(str(pth), topdown=True, onerror=None, followlinks=False)
    for (dirpath, dirnames, filenames) in l:
        for f in filenames:
            if f.endswith(".bib"):
                bibfiles.append(str(Path(dirpath, f)))
    return bibfiles


def process_months(params):
    stems = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct', 'nov','dec']

    def to_numeric(key):
        for i, v in enumerate(stems):
            if v in params[key]:
                params[key] = str(i)
                break

    if 'month' in params:
        to_numeric('month')
    elif 'Month' in params:
        to_numeric('Month')
    return params


def read_records(pth: Path) -> BibDatabase:
    """
    Retrieve citation record key and the whole record from .bib file.
    :param pth: .bib file
    :return: dict where keys are the record keys and values the whole records
    """
    record = "@" + pp.Word(pp.alphanums) + pp.original_text_for(pp.nested_expr("{", "}"))
    parsed = record.parse_string("the string")

    with open(pth) as bibtex_file:
        try:
            bib_database = bibtexparser.load(bibtex_file, parser)
        except UndefinedString:
            print(f'UndefinedString exception on: {pth}')
            raise

    return bib_database


def merge_records(records: Dict[str, dict], duplicates: Dict[str, dict], new_records: BibDatabase) -> None:
    """
    Borrows records and duplicates and merges them with new_records to have distinct keys in records.
    Note: In this version, it processes only the 'entries' of
    a BibDatabase object (leaves out 'comments', 'preambles', 'strings'] which is TODO)
    :param records: records with distinct keys
    :param duplicates: records with keys that were already in records
    :param new_records: a BibDatabase object that is to be merged
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


def write_records(records: Dict[str, dict], output_name: str) -> None:
    """
    Writes the records to a file.
    Note: In this version, it writes out only the 'entries' of
    a BibDatabase object (leaves out 'comments', 'preambles', 'strings'] which is TODO)
    :param records: dict (bib record key, bib record entry object)
    :param output_name: out put file name (will be created or overwritten!)
    :return: None
    """
    new_bd: BibDatabase = BibDatabase()
    new_bd.entries = records.values()

    # not sure if I could use the 'with' env.
    f = open(output_name, "w")
    bibtexparser.dump(new_bd, f)
    f.close()


def run(pth: Path, output_name: str) -> None:
    """
    Run the script. It searches a directory for all .bib files and merges them to one file with unique records.
    Furthermore, it outputs all the records with duplicate keys into another file.
    :param pth: path to the directory, where the recursive search for .bib files starts
    :param output_name: output file name (will be created or overwritten!)
    :return:
    """
    bibs = search_dir(pth)

    records = {}
    duplicates = {}

    for p in bibs:
        recs = read_records(Path(p))
        merge_records(records, duplicates, recs)
    write_records(records, output_name)
    write_records(duplicates, output_name.split(".")[0] + "_duplicates." + output_name.split(".")[1])


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Less than 2 args. Specify: root directory, output name")
        sys.exit()

    if not os.path.exists(sys.argv[1]):
        print("Invalid root directory")
        sys.exit()

    if len(sys.argv) == 3:
        run(Path(sys.argv[1]), sys.argv[2])
    else:
        print("More than 2 args. Specify: root directory, output name")
        sys.exit()


