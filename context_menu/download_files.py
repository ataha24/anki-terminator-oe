# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

# import imghdr
import os
import uuid

from aqt import QAction, QCursor, QMenu, QTimer, QWebEngineContextMenuRequest, QWebEnginePage, mw
from aqt.utils import tooltip
from aqt.operations import CollectionOp
from anki.collection import Collection

try:
    from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
    pyqt_6 = True
except ImportError:
    pyqt_6 = False

from typing import TYPE_CHECKING
if TYPE_CHECKING: from ..dock_web_view import ResizableWebView, CustomWebEngineView

selected_note_data = None

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp", "avif", "svg"}
AUDIO_EXTENSIONS = {"mp3", "wav", "ogg", "flac", "aac"}
VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "flv", "wmv"}


def get_selected_note_data():
    return selected_note_data


def reset_selected_note_data():
    global selected_note_data
    selected_note_data = None
    print("rest selected_note_data")


def on_download_requested(download: "QWebEngineDownloadRequest", webview:"ResizableWebView"):
    if not pyqt_6:
        return

    file_name = download.downloadFileName()
    print(file_name)
    file_ex = file_name.split('.')[-1] if '.' in file_name else None
    print(file_ex)
    if not file_ex:
        print("file_extension None")
        # return

    if file_ex in IMAGE_EXTENSIONS:
        print("Image file")
    elif file_ex in AUDIO_EXTENSIONS:
        print("Audio file")
        "[sound:{}]"
    elif file_ex in VIDEO_EXTENSIONS:
        print("Video file")
    else:
        print("Unknown file type")
        # return

    unique_filename = f"{uuid.uuid4().hex}.{file_ex}" if file_ex else f"{uuid.uuid4().hex}"
    media_folder = mw.col.media.dir()

    # import os
    # from ..path_manager import USER_FILES
    # download_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), USER_FILES, "download")
    # if not os.path.exists(download_folder):
    #     os.makedirs(download_folder)

    download.setDownloadFileName(unique_filename)
    download.setDownloadDirectory(media_folder)

    if get_selected_note_data():
        note, field = get_selected_note_data()
        context_menu(note, field, download, unique_filename)
        global selected_note_data
        selected_note_data = None
        return

    menu = QMenu(webview)
    if mw.state == 'review':
        note = mw.reviewer.card.note()
        fields = note.keys()
        # for field in fields:
        for index, field in enumerate(fields, start=1):
            # custom_action = QAction(field, webview)
            custom_action = QAction(f"{index}. {field}", webview)
            custom_action.triggered.connect(
                lambda _, field=field: context_menu(note, field, download, unique_filename))
            menu.addAction(custom_action)
    action = menu.exec(QCursor.pos())
    if action is None:
        print("No action selected")
        media_path = os.path.join(media_folder + unique_filename)
        if os.path.exists(media_path):
            os.remove(media_path)

def set_context_menu_v2(webview:"CustomWebEngineView", menu:QMenu):
    global selected_note_data
    selected_note_data = None
    if mw.state == 'review':
        def save_selected_note_field(note, field, webview:"CustomWebEngineView"):
            global selected_note_data
            data = webview.lastContextMenuRequest()
            if (webview.pageAction(QWebEnginePage.WebAction.CopyImageToClipboard).isEnabled()
            and data.mediaType() !=  QWebEngineContextMenuRequest.MediaType.MediaTypeNone):
                webview.triggerPageAction(QWebEnginePage.WebAction.DownloadMediaToDisk)
                selected_note_data = (note, field)
                QTimer.singleShot(5000, reset_selected_note_data)

            print(f"v2-editFlags: {data.editFlags()}")
            print(f"v2-mediaFlags: {data.mediaFlags()}")
            print(f"v2-mediaType: {data.mediaType()}")
            print(f"v2-linkUrl: {data.linkUrl()}")
            print(f"v2-selectedText: {data.selectedText()}")

        note = mw.reviewer.card.note()
        fields = note.keys()
        # for field in fields:
        for index, field in enumerate(fields, start=1):
            # custom_action = QAction(field, webview)
            custom_action = QAction(f"{index}. {field}", webview)
            custom_action.triggered.connect(
                lambda _, field=field: save_selected_note_field(note, field, webview))
            menu.addAction(custom_action)
    # action = menu.exec(QCursor.pos())
    # if action:

    # else:
    #     print("No action selected")
    #     global selected_note_data
    #     selected_note_data = None



def context_menu(note, field, download: "QWebEngineDownloadRequest", filename=None):
    print(download.downloadDirectory())
    print(download.downloadFileName())

    download.isFinishedChanged.connect(lambda : on_download_finished(download, filename, note, field))
    download.accept()

def on_download_finished(download: "QWebEngineDownloadRequest", filename, note, field):
    if download.isFinished():
        if not download.state() == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            tooltip(f"Failed :-( \n {download.interruptReasonString()}")
            return

    if not filename:
        return

    CollectionOp(
        parent=mw,
        op=lambda col: add_image_to_card(filename, note, field, col),
    ).success(
        lambda _: on_success(mw),
    ).run_in_background()

def add_image_to_card(filename, note, field, col: "Collection"):
    config = mw.addonManager.getConfig(__name__)

    file_ex = filename.split('.')[-1] if '.' in filename else None

    if file_ex == None:
        # https://github.com/h2non/filetype.py
        from ..bundle.filetype import filetype
        fullpath = os.path.join(mw.col.media.dir(), filename)
        if os.path.exists(fullpath):
            kind = filetype.guess(fullpath)
            if not kind is None:
                print('filetype, extension: %s' % kind.extension)
                file_ex = kind.extension

                if file_ex:
                    filename = f"{filename}.{file_ex}" if file_ex else f"{filename}"
                    new_fullpath = os.path.join(mw.col.media.dir(), filename)
                    os.rename(fullpath, new_fullpath)

    add_br = ""
    if not note[field].strip() == "":
        add_br = "<br>"

    if file_ex in IMAGE_EXTENSIONS:
        print("Image file")
        width = config.get("image_width", 300)
        if width == 0 :
            fix_width = ""
        else:
            fix_width = f'width="{width}"'
        note[field] += f"{add_br}<img src={filename} {fix_width}>"

    elif file_ex in AUDIO_EXTENSIONS:
        print("Audio file")
        note[field] += f"{add_br}[sound:{filename}]"
    elif file_ex in VIDEO_EXTENSIONS:
        print("Video file")
        note[field] += f"{add_br}[sound:{filename}]"
    else:
        print("Unknown file type")
        note[field] += f"{add_br}{filename}"

    return col.update_note(note)


def on_success(mw) -> None:
    tooltip(msg="🤖 Success!", parent=mw)

