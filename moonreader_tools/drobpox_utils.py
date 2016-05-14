def filepaths_from_metadata(meta):
    """Extracts paths from dropbox metadata objects"""
    return [d['path'] for d in meta['contents']]


def dicts_from_pairs(client, pairs):
    """This method requires rewriting"""
    dicts = []

    for i, pair in enumerate(pairs):
        handle_download(client, dicts, pair, i)
    return dicts


def handle_download(client, dicts, pair, i):
    """This method requires rewriting"""
    d = {}
    print("Obtaining book no {}".format(i))
    if not pair[0]:
        fobj, meta = client.get_file_and_metadata(pair[1])
        d["stat_file"] = meta['path'], fobj
        d["note_file"] = '', None
    elif not pair[1]:
        fobj, meta = client.get_file_and_metadata(pair[0])
        d["note_file"] = meta['path'], fobj
        d["stat_file"] = '', None
    else:
        f_1, meta_1 = client.get_file_and_metadata(pair[0])
        f_2, meta_2 = client.get_file_and_metadata(pair[1])
        d["note_file"] = meta_1['path'], f_1
        d["stat_file"] = meta_2['path'], f_2
    dicts.append(d)
