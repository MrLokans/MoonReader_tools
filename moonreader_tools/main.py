"""
This file contains entry poin for the CLI.
"""
import os
import json
import pprint
import argparse

from moonreader_tools.books import MoonReaderBookData
from moonreader_tools.utils import get_moonreader_files, get_same_book_files


def parse_args():
    parser = argparse.ArgumentParser(description="Main parser")
    parser.add_argument('--path', help="Path to get data from", default=".")
    parser.add_argument('--output-file', help="File to place parsed data.")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.path:
        if not os.path.exists(args.path):
            raise OSError("Specified path does not exist.")
        if not os.path.isdir(args.path):
            raise ValueError("Folder should be specified.")

        moonreader_files = get_moonreader_files(args.path)
        tuples = get_same_book_files(moonreader_files)
        books = [MoonReaderBookData._from_file_tuple(x) for x in tuples]
        book_dict = {"books": [book.to_dict() for book in books]}
        if args.output_file:
            with open(args.output_file, "w") as result_f:
                json.dump(book_dict, result_f, ensure_ascii=False)
        else:
            pprint.pprint(book_dict, indent=2, width=120)


if __name__ == '__main__':
    main()
