"""
This file contains entry poin for the CLI.
"""
import os
import json
import pprint
import argparse
import logging

import dropbox

from .conf import DEFAULT_DROPBOX_PATH, log_format

from moonreader_tools.handlers import DropboxDownloader, FilesystemDownloader


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
    # Handle dropbox book data obtaining
    if args.dropbox_token:
        client = dropbox.Dropbox(args.dropbox_token)
        handler = DropboxDownloader(client, workers=args.workers)
        books = handler.get_books(book_count=args.book_count)
        book_list = [book.to_dict() for book in books]
        book_dict = {"books": book_list}
        if args.output_file:
            with open(args.output_file, "w") as result_f:
                json.dump(book_dict, result_f, ensure_ascii=False)
        pprint.pprint(book_dict)

    # Handle local book data obtaining
    if args.path:

        if not os.path.exists(args.path):
            raise OSError("Specified path does not exist.")
        if not os.path.isdir(args.path):
            raise ValueError("Folder should be specified.")

        handler = FilesystemDownloader()
        books = handler.get_books(path=args.path)

        book_dict = {"books": [book.to_dict() for book in books]}
        if args.output_file:
            with open(args.output_file, "w") as result_f:
                json.dump(book_dict, result_f, ensure_ascii=False)
        else:
            pprint.pprint(book_dict, indent=2, width=120)


if __name__ == "__main__":
    main()
