# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>


# not used yet :-O

import base64
import os
import re
import uuid

# import imghdr

import requests

from aqt import AnkiQt, QAction, QEventLoop, QWebEnginePage, mw, QMenu, QWebEngineView, QWebEngineProfile
from aqt.utils import tooltip
from anki.notes import Note
from aqt.operations import CollectionOp
from anki.collection import Collection

from PyQt6.QtCore import QUrl
from PyQt6.QtNetwork import (QNetworkAccessManager, QNetworkCookieJar, QNetworkCookie, QNetworkRequest,
                            QNetworkReply, QNetworkDiskCache)
# https://doc.qt.io/qt-6/qnetworkaccessmanager.html
from aqt import mw

# https://github.com/h2non/filetype.py
from ..bundle.filetype import filetype


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

HEADER_B = b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

# HEADER_B = b"Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"

def get_image_data(imageUrl:QUrl = "", cookie_profile:"QWebEngineProfile"=None) -> str:
    if not imageUrl:
        return None
    print("get images")

    url_str = imageUrl.toString()
    if url_str.startswith("data:image"):
        base64_data = re.sub('^data:image/.+;base64,', '', url_str)
        image_data = base64.b64decode(base64_data)

        kind = filetype.guess(image_data)
        if kind and kind.mime.startswith('image/'):
            ext = kind.extension
        else:
            return None

        # image_format = imghdr.what(None, image_data)
        # if image_format:
        #     ext = '.' + image_format
        # else:
        #     return None

        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_name = mw.col.media.write_data(unique_filename, image_data)
        return file_name


    # 🍪for get images
    print(">>>for get images")
    cookie_manager = QNetworkAccessManager()
    cookie_jar = QNetworkCookieJar()
    cookie_manager.setCookieJar(cookie_jar)

    cache_path = cookie_profile.cachePath()
    print(f"cache_path: {cache_path}")
    disk_cache = QNetworkDiskCache()
    disk_cache.setCacheDirectory(cache_path)
    cookie_manager.setCache(disk_cache)

    web_cookie_store = cookie_profile.cookieStore()
    def set_cookies_to_jar(cookie:QNetworkCookie):
        cookie_jar.setCookiesFromUrl([cookie], QUrl(cookie.domain()))
    web_cookie_store.cookieAdded.connect(set_cookies_to_jar)

    request = QNetworkRequest(imageUrl)
    current_header = cookie_profile.httpUserAgent()
    print(current_header)
    
    # request.setRawHeader(b"User-Agent", HEADER_B)
    request.setRawHeader(b"User-Agent", current_header.encode('utf-8'))
    response = cookie_manager.get(request)

    loop = QEventLoop()
    response.finished.connect(loop.quit)
    loop.exec()
    web_cookie_store.cookieAdded.disconnect(set_cookies_to_jar)

    status_code = response.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
    print(f"status_code: {status_code}")
    redirect_url = response.attribute(QNetworkRequest.Attribute.RedirectionTargetAttribute)

    if response.error() != QNetworkReply.NetworkError.NoError:
        print(response.error())
        return None

    content_bytes = response.readAll().data()
    print(f"content_bytes: {content_bytes}")

    # response = requests.get(imageUrl.toString(), headers=HEADERS, timeout=10, allow_redirects=False)
    # html_content = response.text
    # print(html_content)
    # return None

    # if response.status_code != 200:
    #     return None

    # image_format = imghdr.what(None, response.content)

    kind = filetype.guess(content_bytes)
    if kind and kind.mime.startswith('image/'):
        ext = kind.extension
    else:
        return None

    # image_format = imghdr.what(None, content_bytes)
    # print(f"image_format: {image_format}")
    # if image_format:
    #     ext =  '.' + image_format
    # else:
    #     return None

    unique_filename = f"{uuid.uuid4().hex}{ext}"
    # file_name = mw.col.media.write_data(unique_filename, response.content)
    file_name = mw.col.media.write_data(unique_filename, content_bytes)
    return file_name


def add_image_context_menu(webview:QWebEngineView, menu: QMenu, cookie_manager, *args,**kwargs):
    if mw.state == 'review':
        note = mw.reviewer.card.note()
        fields = note.keys()
        # for field in fields:
        for index, field in enumerate(fields, start=1):
            # custom_action = QAction(field, webview)
            custom_action = QAction(f"{index}. {field}", webview)
            custom_action.triggered.connect(
                lambda _, f=field: context_menu(note, webview, f, cookie_manager))
            menu.addAction(custom_action)

def context_menu(note, webview:QWebEngineView, field, cookie_manager, *args,**kwargs):
    imageUrl = webview.lastContextMenuRequest().mediaUrl()
    if not imageUrl:
        return
    if not isinstance(imageUrl, QUrl) or imageUrl.toString().strip() == "":
        return None

    CollectionOp(
        parent=mw,
        op=lambda col: add_image_to_card(note, field, imageUrl, cookie_manager, col),
    ).success(
        lambda _: on_success(mw),
    ).run_in_background()

def add_image_to_card(note:Note, field, imageUrl:QUrl, cookie_manager, col: "Collection"):
    filename = get_image_data(imageUrl, cookie_manager)
    if not filename:
        return
    config = mw.addonManager.getConfig(__name__)
    add_br = ""
    if not note[field].strip() == "":
        add_br = "<br>"

    width = config.get("image_width", 300)
    if width == 0 :
        fix_width = ""
    else:
        fix_width = f'width="{width}"'
    note[field] += f"{add_br}<img src={filename} {fix_width}>"
    return col.update_note(note)

def on_success(mw:AnkiQt) -> None:
    tooltip(msg="🤖 Success!", parent=mw)

