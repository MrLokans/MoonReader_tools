import zlib


class FileReader(object):
    """
    A mixin class able to read simple and gzipped
    files
    """

    @classmethod
    def read_file_obj(cls, flike_obj) -> str:
        """Creates note object from file-like object"""
        content = flike_obj.read()
        if cls._is_zipped(content):
            content = cls._read_zipped_content(content)
        else:
            content = content
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        return content

    @classmethod
    def _read_zipped_content(cls, str_content) -> bytes:
        """Creates note object from zip-compressed string"""
        if not cls._is_zipped:
            raise ValueError("Given string is not zipped.")
        return cls._unpack_str(str_content)

    @staticmethod
    def _unpack_str(zipped_str) -> bytes:
        """Decompresses zipped string"""
        return zlib.decompress(zipped_str)

    @staticmethod
    def _is_zipped(str_text: str) -> bool:
        """Checks whether given sequence is compressed with zip"""
        if len(str_text) < 2:
            return False
        return (str_text[0], str_text[1]) == (int("78", base=16), int("9c", base=16))
