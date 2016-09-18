from moonreader_tools.accessors.pdf_accessor import PDFAccessor
from moonreader_tools.accessors.fb2_accessor import FB2Accessor


class IncorrectBookType(Exception):
    pass


def accessor_cls_by_type(book_type):
    _type = book_type.lower()
    if _type.lower in {'fb2', 'epub', 'mobi', 'txt'}:
        return FB2Accessor
    elif _type in {'pdf', }:
        return PDFAccessor
    else:
        msg = "Unknown book type: {}"
        raise IncorrectBookType(msg.format(_type))
