# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

from aqt import AnkiQt, QAction, QWebEnginePage, mw, QMenu, QWebEngineView
from aqt.utils import tooltip
# from aqt.operations import QueryOp
from anki.notes import Note
from aqt.operations import CollectionOp
from anki.collection import Collection


def add_context_menu(webview:QWebEngineView , menu: QMenu,*args,**kwargs):
    if webview.pageAction(QWebEnginePage.WebAction.Copy).isEnabled():

        if mw.state == 'review':
            note = mw.reviewer.card.note()
            fields = note.keys()
            # for field in fields:
            for index, field in enumerate(fields, start=1):
                # custom_action = QAction(field, webview)
                custom_action = QAction(f"{index}. {field}", webview)
                custom_action.triggered.connect(
                    lambda _, f=field: context_menu(note, webview, f))
                menu.addAction(custom_action)


def context_menu(note, webview:QWebEngineView, field, *args,**kwargs):
    selected = webview.page().selectedText()
    if not selected:
        return
    if not isinstance(selected, str) or selected.strip() == "":
        return None
    launch_bg_note_processing(note, field, selected)

def launch_bg_note_processing(note, field, selected):
    CollectionOp(
        parent=mw,
        op=lambda col: _add_text_to_card(note, field, selected, col),
    ).success(
        lambda _: on_success(mw),
    ).run_in_background()

    # op = QueryOp(
    #     parent=mw,
    #     op=lambda _: _add_text_to_card(note, field, selected, mw),
    #     success=lambda _: on_success(mw),
    # )
    # message = f"🤖 Now loading..."
    # op.with_backend_progress(message).run_in_background()



def _add_text_to_card(note:Note, field, selected:str, col: "Collection"):
    add_br = ""
    if not note[field].strip() == "":
        add_br = "<br>"
    print(repr(selected))
    selected = selected.replace("\n", "<br>")
    note[field] += "".join('{add_br}{add_text}'.format(add_br=add_br, add_text=selected))

    return col.update_note(note)

def on_success(mw:AnkiQt) -> None:
    tooltip(msg="🤖 Success!", parent=mw)

