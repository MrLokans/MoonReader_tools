import datetime

from moonreader_tools.notes import Note, NoteStyle


def test_valid_defaults_for_note():
    name, now, note = "text", datetime.datetime.utcnow(), "Some remark"
    n = Note(text="text", created=now, note=note)

    assert n.text == name
    assert n.created == now
    assert n.style == NoteStyle.SELECTED
    assert n.color == (0, 255, 255, 255)
    assert n.note == note
