"""
This file contains entry poin for the CLI.
"""
import os
import json
import pprint
import argparse
import logging


from .conf import DEFAULT_DROPBOX_PATH, log_format

from moonreader_tools.books import Book
from moonreader_tools.handlers import DropboxDownloader
from moonreader_tools.utils import (
    get_moonreader_files,
    get_same_book_files
)


logging.basicConfig(format=log_format, filename="moonreader.log")


def parse_args():
    parser = argparse.ArgumentParser(description="Main parser")
    parser.add_argument('--path', help="Path to get data from", default=".")
    parser.add_argument('--output-file', help="File to place parsed data.")
    parser.add_argument('--dropbox-token',
                        help='Token to access your dropbox account')
    parser.add_argument('--dropbox-path',
                        default=DEFAULT_DROPBOX_PATH,
                        help='Token to access your dropbox account')
    parser.add_argument('--book-count',
                        default=50,
                        type=int,
                        help='Number of books to get data about from dropbox.')
    parser.add_argument('--workers',
                        default=8,
                        type=int,
                        help='Number of threads/processes to use.')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.dropbox_token:
        handler = DropboxDownloader(access_token=args.dropbox_token,
                                    workers=args.workers)
        books_data = handler.get_books(book_count=args.book_count)
        pprint.pprint(books_data)
    if args.path:

        if not os.path.exists(args.path):
            raise OSError("Specified path does not exist.")
        if not os.path.isdir(args.path):
            raise ValueError("Folder should be specified.")

        moonreader_files = get_moonreader_files(args.path)
        tuples = get_same_book_files(moonreader_files)
        books = [Book.from_file_tuple(x) for x in tuples]
        book_dict = {"books": [book.to_dict() for book in books]}
        if args.output_file:
            with open(args.output_file, "w") as result_f:
                json.dump(book_dict, result_f, ensure_ascii=False)
        else:
            pprint.pprint(book_dict, indent=2, width=120)


if __name__ == '__main__':
    try:
        main()
    finally:
        log = logging.getLogger('urllib3.connectionpool')
        log.setLevel(logging.WARNING)
