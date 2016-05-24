Description - what, why and how
===========
This library allows you to parse and write back Moon+Reader notes and statistics files either local or remote (Dropbox one).

[Moon+Reader](https://play.google.com/store/apps/details?id=com.flyersoft.moonreader) is one of the best ebook readers I've tried for Android OS with lots of functionality. The features I use a lot are creating notes when reading books and having them syncronized with my dropbox account. One day I thought that it would be great to write a library for parsing those files and obtaining data from them, as a result this library is being developed. 

Installation from source
========================
```bash
git clone https://github.com/MrLokans/MoonReader_tools
cd MoonReader_tools
python setup.py install
```

Installation from PyPI
======================
```bash
pip install moonreader_tools
```

Usage
=====
It is assumed that you're the MoonReader+ Pro user and have Dropbox linked to your reader app.
If you're reading and creating highlights you'll be having lots of files in the syncronized folder (e.g. Dropbox/Books/.Moon+/Cache)

To get JSON data about all of your books you may use CLI entry to get data from dropbox or local folder:

```bash
moon_tools --path <path/to/moonreader/cache> --output-file <outfile>.json
```
```bash
moon_tools --dropbox-token <DROPBOT TOKEN> --output-file <outfile>.json

To be continued...