import os
import sys
from collections import namedtuple
from pathlib import Path
import pyparsing as pp
from typing import Dict, Tuple, List

Record = namedtuple("Record", ["body", "type"])


def search_dir(pth: Path) -> List[Path]:
    """
    Search directory for files with .bib suffix.
    :param pth: start search here
    :return: list of .bib file paths
    """
    bibfiles = []
    found = os.walk(str(pth), topdown=True, onerror=None, followlinks=False)
    for (dirpath, dirnames, filenames) in found:
        for f in filenames:
            if f.endswith(".bib"):
                bibfiles.append(Path(dirpath, f))
    return bibfiles


def read_records(pth: Path) -> Dict[str, Record]:
    """
    Retrieve citation record key and the whole record and its type from .bib file.
    :param pth: .bib file
    :return: dict where keys are the record keys and values the tuples(record type, whole records incl. {})
    """
    record_rule = "@" + pp.Word(pp.alphanums) + pp.original_text_for(pp.nested_expr("{", "}"))
    file_rule = pp.ZeroOrMore(record_rule)
    body = pp.common.comma_separated_list

    # we need to strip the {} from the record. Nobody has a better solution yet:
    # https://stackoverflow.com/questions/76020762/pyparsing-how-to-match-parentheses-around-comma-separated-list
    strip_body = lambda l: l[1:-1]

    file_content = pth.read_text()
    try:
        parsed = file_rule.parse_string(file_content)
        types = parsed[1::3]
        bodies = parsed[2::3]

        # key must be on the first position otherwise it's not a valid record
        keys = [x[0] for x in [body.parse_string(strip_body(x)) for x in bodies]]

        return dict(zip(keys, [Record(b, t) for b, t in zip(bodies, types)]))
    except Exception as e:
        # append a message to the stacktrace https://stackoverflow.com/a/71605371/245543
        if len(e.args) >= 1:
            e.args = (e.args[0] + "Parsing exception for file: " + str(pth),) + e.args[1:]
        raise


def merge_records(records: Dict[str, Record], duplicates: Dict[str, Record],
                  new_records: Dict[str, Record]) -> None:
    """
    Borrows records and duplicates and merges them with new_records to have distinct keys in records.
    :param records: records with distinct keys
    :param duplicates: records with keys that were already in records
    :param new_records: records to be merged
    :return: None
    """
    for k, v in new_records.items():
        if k in records:
            i = 0
            suffix = "_" + str(i)
            while k + suffix in duplicates:
                i += 1
                suffix = "_" + str(i)
            duplicates[k + suffix] = v
        else:
            records[k] = v


def write_records(records: Dict[str, Record], output_path: Path) -> None:
    """
    Writes the records to a file.
    :param records: dict (bib record key, bib record entry object)
    :param output_name: out put file name (will be created or overwritten!)
    :return: None
    """
    with open(output_path, 'w') as f:
        for k, v in records.items():
            f.write(f"@{v.type}{v.body}\n")


def run(pth: Path, output_path: Path) -> None:
    """
    Run the script. It searches a directory for all .bib files and merges them to one file with unique records.
    Furthermore, it outputs all the records with duplicate keys into another file.
    :param pth: path to the directory, where the recursive search for .bib files starts
    :param output_path: output file name (will be created or overwritten!)
    :return:
    """
    bib_files = search_dir(pth)

    records = {}
    duplicates = {}

    for p in bib_files:
        recs = read_records(Path(p))
        merge_records(records, duplicates, recs)
    write_records(records, output_path)
    write_records(duplicates,
                  Path(output_path.parent, output_path.name.split(".")[0] + "_duplicates" + output_path.suffix))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Less than 2 args. Specify: root directory, output name")
        sys.exit()

    if not os.path.exists(sys.argv[1]):
        print("Invalid root directory")
        sys.exit()

    if len(sys.argv) == 3:
        run(Path(sys.argv[1]), Path(sys.argv[2]))
    else:
        print("More than 2 args. Specify: root directory, output name")
        sys.exit()


