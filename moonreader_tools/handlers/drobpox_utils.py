import io
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed

# urllib3 produces noisy exceptions we disable
logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def extract_book_paths_from_dir_entries(entries):
    """Extracts paths from dropbox metadata objects"""
    return [entry.path_lower for entry in entries]


def dicts_from_pairs(client, pairs, workers=8):
    """This method requires rewriting"""
    futures = set()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for i, pair in enumerate(pairs):
            future = executor.submit(get_book_dict, client, pair)
            futures.add(future)
        try:
            for future in as_completed(futures):
                err = future.exception()
                if err is None:
                    yield future.result()
                else:
                    err_msg = "Error obtaining book dictionary data: {}"
                    logger.error(err_msg.format(err))
        except KeyboardInterrupt:
            for future in futures:
                future.cancel()
            executor.shutdown()


def get_book_dict(client, pair):
    """This method requires rewriting"""
    book_files_dict = {}
    if not pair[0]:
        metadata, response = client.files_download(pair[1])
        book_files_dict["stat_file"] = (
            metadata.path_display,
            io.BytesIO(response.content),
        )
        book_files_dict["note_file"] = "", None
    elif not pair[1]:
        metadata, response = client.files_download(pair[0])
        book_files_dict["note_file"] = (
            metadata.path_display,
            io.BytesIO(response.content),
        )
        book_files_dict["stat_file"] = "", None
    else:
        metadata_0, response_0 = client.files_download(pair[0])
        metadata_1, response_1 = client.files_download(pair[1])
        book_files_dict["note_file"] = (
            metadata_0.path_display,
            io.BytesIO(response_0.content),
        )
        book_files_dict["stat_file"] = (
            metadata_1.path_display,
            io.BytesIO(response_1.content),
        )
    return book_files_dict
