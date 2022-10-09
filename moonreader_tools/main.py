"""
This file contains entry poin for the CLI.
"""
import argparse
import json
import logging
import os
import pprint

import dropbox

from moonreader_tools.finders import DropboxFinder, FilesystemFinder

from .conf import DEFAULT_DROPBOX_PATH, log_format

logging_handlers = [logging.StreamHandler(), logging.FileHandler("moonreader.log")]

logging.basicConfig(format=log_format, handlers=logging_handlers, level=logging.DEBUG)


def parse_args():
    parser = argparse.ArgumentParser(description="Main parser")
    parser.add_argument("--path", help="Path to get data from", default=".")
    parser.add_argument("--output-file", help="File to place parsed data.")
    parser.add_argument("--dropbox-token", help="Token to access your dropbox account")
    parser.add_argument(
        "--dropbox-path",
        default=DEFAULT_DROPBOX_PATH,
        help="Token to access your dropbox account",
    )
    parser.add_argument(
        "--book-count",
        default=50,
        type=int,
        help="Number of books to get data about from dropbox.",
    )
    parser.add_argument(
        "--workers", default=8, type=int, help="Number of threads/processes to use."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.dropbox_token:
        client = dropbox.Dropbox(args.dropbox_token)
        finder = DropboxFinder(client, workers=args.workers)
    elif args.path:
        if not os.path.exists(args.path):
            raise OSError("Specified path does not exist.")
        if not os.path.isdir(args.path):
            raise ValueError("Folder should be specified.")
        finder = FilesystemFinder(path=args.path)
    else:
        return
    books = finder.get_books()
    book_dict = {"books": [book.to_dict() for book in books]}
    if args.output_file:
        with open(args.output_file, "w") as result_f:
            json.dump(book_dict, result_f, ensure_ascii=False)
    else:
        pprint.pprint(book_dict, indent=2, width=120)


if __name__ == "__main__":
    main()
