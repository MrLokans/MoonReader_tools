import logging

from concurrent.futures import ThreadPoolExecutor, as_completed

# urllib3 produces noisy exceptions we disable
log = logging.getLogger('urllib3.connectionpool')
log.setLevel(logging.CRITICAL)


def filepaths_from_metadata(meta):
    """Extracts paths from dropbox metadata objects"""
    return [d['path'] for d in meta['contents']]


def dicts_from_pairs(client, pairs, workers=8):
    """This method requires rewriting"""
    dicts = []
    futures = set()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        for i, pair in enumerate(pairs):
            future = executor.submit(get_book_dict, client, pair)
            futures.add(future)
        try:
            for future in as_completed(futures):
                err = future.exception()
                if err is None:
                    dicts.append(future.result())
                else:
                    err_msg = "Error occured when obtaining book data: {}"
                    print(err_msg.format(str(err)))
        except KeyboardInterrupt:
            for future in futures:
                future.cancel()
            executor.shutdown()

    return dicts


def get_book_dict(client, pair):
    """This method requires rewriting"""
    book_files_dict = {}
    if not pair[0]:
        fobj, meta = client.get_file_and_metadata(pair[1])
        book_files_dict["stat_file"] = meta['path'], fobj
        book_files_dict["note_file"] = '', None
    elif not pair[1]:
        fobj, meta = client.get_file_and_metadata(pair[0])
        book_files_dict["note_file"] = meta['path'], fobj
        book_files_dict["stat_file"] = '', None
    else:
        f_1, meta_1 = client.get_file_and_metadata(pair[0])
        f_2, meta_2 = client.get_file_and_metadata(pair[1])
        book_files_dict["note_file"] = meta_1['path'], f_1
        book_files_dict["stat_file"] = meta_2['path'], f_2
    return book_files_dict
