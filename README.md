[![Build Status](http://mrlokans.com/jenkins/job/moonreader_tools/badge/icon)](http://mrlokans.com/jenkins/job/moonreader_tools/)

Description - what, why and how
===========
This library allows you to get basic data from Moon+Reader notes and statistics files either local or remote (Dropbox support is currently available).


[Moon+Reader](https://play.google.com/store/apps/details?id=com.flyersoft.moonreader) is one of the best ebook readers I've tried for Android OS with lots of functionality.
The features I use a lot are creating notes when reading books and having them syncronized with my dropbox account. One day I thought that it would be great to write a library for parsing those files and obtaining data from them, as a result this library is being developed. 

Installation from source
========================
This requires [poetry](https://python-poetry.org/) for the installation
```bash
git clone https://github.com/MrLokans/MoonReader_tools
cd MoonReader_tools
poetry build && poetry install
```

Installation from PyPI
======================
```bash
pip install moonreader_tools
```

Usage as CLI utility
====================
It is assumed that you're the MoonReader+ Pro user and have Dropbox linked to your reader app.
If you're reading and creating highlights you'll be having lots of files in the syncronized folder (e.g. Dropbox/Books/.Moon+/Cache)

To get JSON data about all of your books you may use CLI entry to get data from dropbox or local folder:

```bash
moon_tools --path <path/to/moonreader/cache> --output-file <outfile>.json

moon_tools --dropbox-token <DROPBOX TOKEN> --output-file <outfile>.json
```

Usage as library
================

```python
import dropbox
from moonreader_tools.finders import FilesystemFinder, DropboxFinder

# We may look for books in FS directories
extractor = FilesystemFinder(path="/dir/with/moonreader/files")
books = extractor.get_books()
for book in books:
    print(book.title)
    for note in book.notes:
        print(note.text)

# And in the dropbox

client = dropbox.Dropbox(access_token='MYSECRETTOKEN')
extractor = DropboxFinder(client, books_path='moonreader_save_dir')

books = extractor.get_books()
for book in books:
    print(book.title)
    for note in book.notes:
        print(note.text)
```

Running tests
=============
```
make test
```

Formatting codebase
==============
```
make format
```