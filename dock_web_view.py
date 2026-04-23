# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

import os
import random
import time
from aqt.utils import openLink
from aqt import (
QAction, QCheckBox, QClipboard, QComboBox, QDockWidget, QFontMetrics, QGraphicsOpacityEffect,
QKeySequence, QLabel, QLineEdit, QMenu, QMimeData,
QPixmap, QPushButton,  QSize, QTimer, QToolBar, QUrl, QVBoxLayout,
QWebEnginePage,
QWebEngineProfile, QWebEngineSettings, gui_hooks,
QWebEngineView, QWidget, Qt, mw)
from aqt.webview import AnkiWebView
from os.path import join, dirname, exists
from anki.cards import Card

from .config.PopUpAnkiConfig import (
        SOUND_SYSTEM, set_this_addon_Config, CONFIG_FOLDER,
        SOUND_OPEN, SOUND_SELECT,SOUND_OPENLINK, SOUND_OK,
        SOUND_CANCEL, SOUND_SYSTEM,THEME_CHANGE
        )
from .context_menu.download_files import on_download_requested, set_context_menu_v2, reset_selected_note_data


"""
PYGsound(SOUND_OPEN)
PYGsound(SOUND_SELECT)
PYGsound(SOUND_OPENLINK)
PYGsound(SOUND_OK)
PYGsound(SOUND_CANCEL)
PYGsound(SOUND_SYSTEM)
PYGsound(THEME_CHANGE)
"""

from .path_manager import (BING_CHAT, CHAT_GPT, COOKIE_DATA, GOOGLE_BARD, IMAGE_FX, NOW_LOADING,
                            SHOW_ANSWER_PNG, HIDE_HIGHT, USER_FILES, CUSTOM_AI,
                            DEEP_SEEK, PERPLEXITY, CLAUDE,
                            GROK_AI, DUCK_AI,
                            OPEN_EVIDENCE, OPEN_EVIDENCE_URL,
                            THEMES,
                            ADDON_NAME
                            )
from .shigetr import shige_tr, qtip_style

from .context_menu.add_fields import add_context_menu
from .context_menu.get_image import add_image_context_menu

# ── Open Evidence integration ────────────────────────────────────────────────

_OE_INJECT_JS = r"""
(function() {
    var query = OE_QUERY_PLACEHOLDER;
    var selectors = [
        'textarea[placeholder*="ask" i]',
        'textarea[placeholder*="search" i]',
        'input[placeholder*="ask" i]',
        'input[placeholder*="search" i]',
        'input[type="search"]',
        'textarea',
        'input[type="text"]'
    ];
    var input = null;
    for (var i = 0; i < selectors.length; i++) {
        var el = document.querySelector(selectors[i]);
        if (el) { input = el; break; }
    }
    if (!input) return;
    var proto = input.tagName === 'TEXTAREA'
        ? window.HTMLTextAreaElement.prototype
        : window.HTMLInputElement.prototype;
    var setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
    setter.call(input, query);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    input.focus();
    setTimeout(function() {
        input.dispatchEvent(new KeyboardEvent('keydown', {
            key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true
        }));
    }, 80);
})();
"""

_OE_SUFFIX = (
    "\n\nStart with a 2-sentence summary of the most important takeaway, "
    "then provide the full detail below that."
    "\n\nDo not ask follow-up questions, offer to elaborate further, "
    "or suggest that I ask anything else."
)

OE_PRESETS = [
    {
        "label": "Mechanism",
        "template": (
            'I am a medical student studying the Anki flashcard "{}" '
            "for USMLE Step 1/2 and class exams. "
            "Explain the core mechanism behind this concept, focusing on the causal chain that matters most."
        ),
    },
    {
        "label": "Board Pearl",
        "template": (
            'I am a medical student studying the Anki flashcard "{}" '
            "for USMLE Step 1/2 and class exams. "
            "Give me the highest-yield facts about this topic most likely to appear on boards, "
            "including classic buzzwords and associations."
        ),
    },
    {
        "label": "Distinguish",
        "template": (
            'I am a medical student studying the Anki flashcard "{}" '
            "for USMLE Step 1/2 and class exams. "
            "Explain the key features that distinguish this from the conditions or concepts "
            "most commonly confused with it."
        ),
    },
    {
        "label": "Presentation",
        "template": (
            'I am a medical student studying the Anki flashcard "{}" '
            "for USMLE Step 1/2 and class exams. "
            "Describe the classic clinical presentation and the most important "
            "diagnostic findings or test results I should know."
        ),
    },
    {
        "label": "Management",
        "template": (
            'I am a medical student studying the Anki flashcard "{}" '
            "for USMLE Step 1/2 and class exams. "
            "Explain the first-line treatment and key management principles, "
            "including must-know drug mechanisms or contraindications."
        ),
    },
]


def _oe_extract_card_text(card, max_chars: int = 350) -> str:
    """Extract first-field plain text from an Anki card for OE queries."""
    import re
    from html.parser import HTMLParser

    class _S(HTMLParser):
        def __init__(self):
            super().__init__()
            self._parts = []
        def handle_data(self, data):
            self._parts.append(data)
        def get_text(self):
            return " ".join(self._parts)

    try:
        note = card.note()
        fields = list(note.items())
        if not fields:
            return ""
        raw = fields[0][1]
        s = _S()
        s.feed(raw)
        text = s.get_text()
        text = re.sub(r"\{\{c\d+::(.*?)(?:::.*?)?\}\}", r"\1", text)
        text = " ".join(text.split())
        return text[:max_chars].strip()
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────

web_shortcut = None
completely_close_sidebar = None

SYMBOL = {
    "single_quotation": ["'","'"],
    "brackets": ["[","]"],
    "parentheses": ["(",")"],
    "braces": ["{","}"],
    "angle_brackets": ["<",">"],
    "none": ["",""],
    "bold_md": [" **","** "],
    "bold_html": ["<b>","</b>"],
    "span_translation_no": ["<span translation=\"no\">","</span>"],
} # どれも効果がありません¯\_(ﾂ)_/¯

CHOICE_SYMBOL = "single_quotation"

# def handle_new_window(url):
#     openLink(url)

class CustomWebEnginePage(QWebEnginePage):
    def createWindow(self, _type):
        print(_type)

        profile = self.profile()

        # if _type == QWebEnginePage.WebWindowType.WebDialog:
        if True:
            mw.AnkiTerminator_new_dialog = new_dialog = QWidget(None)
            new_dialog.setWindowTitle("New Dialog")
            new_dialog.resize(500, 600)
            web_view = CustomWebEngineView(new_dialog)
            new_page = CustomWebEnginePage(profile, web_view)
            web_view.setPage(new_page)
            layout = QVBoxLayout(new_dialog)
            layout.addWidget(web_view)
            new_dialog.setLayout(layout)
            QTimer.singleShot(0, new_dialog.show)
            # mw.AnkiTerminator_new_dialog.show()
        # else:
        # # new_page.urlChanged.connect(handle_new_window)
        #     new_page = CustomWebEnginePage(profile)

        return new_page

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass
        # ﾃﾞﾊﾞｯｸﾞ用
        # try:
        #     if level == QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel:
        #         level_str = "info"
        #     elif level == QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel:
        #         level_str = "warning"
        #     elif level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
        #         level_str = "error"
        #     else:
        #         level_str = str(level)
        # except Exception:
        #     level_str = str(level)
        # print(f"[JS Console][{level_str}] {message} (Line {lineNumber}, Source: {sourceID})")


try:
    from PyQt6.QtWebEngineCore import QWebEngineContextMenuRequest
except ImportError:
    from PyQt5.QtWebEngineWidgets import QWebEngineContextMenuData as QWebEngineContextMenuRequest


class CustomWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent #type: ResizableWebView

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        data = self.lastContextMenuRequest()
        if data.editFlags() & QWebEngineContextMenuRequest.EditFlag.CanPaste:
            is_can_paste = True
        else:
            is_can_paste = False


        if not self.pageAction(QWebEnginePage.WebAction.Copy).isEnabled():
            if self.pageAction(QWebEnginePage.WebAction.Back).isEnabled():
                menu.addAction(self.pageAction(QWebEnginePage.WebAction.Back))
            if self.pageAction(QWebEnginePage.WebAction.Forward).isEnabled():
                menu.addAction(self.pageAction(QWebEnginePage.WebAction.Forward))
            if self.pageAction(QWebEnginePage.WebAction.Reload).isEnabled():
                menu.addAction(self.pageAction(QWebEnginePage.WebAction.Reload))

        if (self.pageAction(QWebEnginePage.WebAction.Paste).isEnabled()
            and is_can_paste):
            menu.addAction(self.pageAction(QWebEnginePage.WebAction.Paste))

        if (not is_can_paste
            and self.pageAction(QWebEnginePage.WebAction.CopyImageToClipboard).isEnabled()
            and data.mediaType() !=  QWebEngineContextMenuRequest.MediaType.MediaTypeNone):
            menu.addAction(self.pageAction(QWebEnginePage.WebAction.CopyImageToClipboard))
            # menu.addAction(self.pageAction(QWebEnginePage.WebAction.DownloadMediaToDisk))
            menu.addSeparator()
            reset_selected_note_data()
            set_context_menu_v2(self, menu)
            menu.addSeparator()

        if self.pageAction(QWebEnginePage.WebAction.Copy).isEnabled():
            menu.addAction(self.pageAction(QWebEnginePage.WebAction.Copy))

            custom_action = QAction("🧩Set text to AnkiTerminator", self)
            custom_action.triggered.connect(
                lambda: self.contextMenu(self, menu))
            menu.addAction(custom_action)

        # menu.addSeparator()
        # text_action = QAction("❔️🤖Paste prompt", menu)
        # text_action.triggered.connect(
        #     lambda: openLink(
        # "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#right-click-actions"))
        # # text_action.setEnabled(False)
        # menu.addAction(text_action)

        # if data.editFlags() & QWebEngineContextMenuRequest.EditFlag.CanPaste:
        #     print("paste")
        #     is_can_paste = True
        #     from .context_menu.past_prompts import make_prompts_menu

        #     menu.addSeparator()
        #     make_prompts_menu(self.parent_window, menu)
        #     menu.addSeparator()
        # else:
        #     is_can_paste = False

        menu.addSeparator()
        text_action = QAction("❔️📥Add text to card", menu)
        text_action.triggered.connect(
            lambda: openLink(
        "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#right-click-actions"))
        # text_action.setEnabled(False)
        menu.addAction(text_action)

        print(f"editFlags: {data.editFlags()}")
        print(f"mediaFlags: {data.mediaFlags()}")
        print(f"mediaType: {data.mediaType()}")
        print(f"linkUrl: {data.linkUrl()}")
        print(f"selectedText: {data.selectedText()}")

        # editFlags: EditFlag.CanTranslate|CanPaste
        # mediaFlags: MediaFlag.0
        # mediaType: MediaType.MediaTypeNone
        # linkUrl: PyQt6.QtCore.QUrl('')
        # selectedText:

        # editFlags: EditFlag.CanTranslate|CanSelectAll
        # mediaFlags: MediaFlag.0
        # mediaType: MediaType.MediaTypeNone
        # linkUrl: PyQt6.QtCore.QUrl('')
        # selectedText:

        # editFlags: EditFlag.CanTranslate|CanSelectAll
        # mediaFlags: MediaFlag.MediaCanPrint
        # mediaType: MediaType.MediaTypeImage
        # linkUrl: PyQt6.QtCore.QUrl('')
        # selectedText:

        # if  (not is_can_paste
        #     and data.mediaFlags() & QWebEngineContextMenuRequest.MediaFlag.MediaCanPrint
        #     and data.mediaType() == QWebEngineContextMenuRequest.MediaType.MediaTypeImage):
        #     imageUrl = self.lastContextMenuRequest().mediaUrl()
        #     print(f"iamge: {imageUrl}")
        #     menu.addSeparator()
        #     add_image_context_menu(self, menu, self.parent_window.cookie_profile)
        #     menu.addSeparator()
        #     pass

        # elif not is_can_paste and self.pageAction(QWebEnginePage.WebAction.Copy).isEnabled():
        if not is_can_paste and self.pageAction(QWebEnginePage.WebAction.Copy).isEnabled():
            selected = self.page().selectedText()
            print(f"text: {selected}")
            menu.addSeparator()
            add_context_menu(self, menu)
            menu.addSeparator()

        from .context_menu.image_widget import make_image_ai_widget, send_prompts, CustomImageWidget
        menu.addSeparator()
        imageFX_action = QAction("🖼️ImageFX", menu)
        imageFX_action.triggered.connect(lambda: make_image_ai_widget(self.parent_window.webpage))
        menu.addAction(imageFX_action)

        if not is_can_paste and self.pageAction(QWebEnginePage.WebAction.Copy).isEnabled():
            selected = self.page().selectedText()
            print(f"text: {selected}")
            send_imageFX_action = QAction("Send Prompt to ImageFX", menu)
            send_imageFX_action.triggered.connect(lambda: send_prompts(selected))
            menu.addAction(send_imageFX_action)
            if (not hasattr(mw, "AnkiTerminator_image_Ai_dialog")
                or
                hasattr(mw, "AnkiTerminator_image_Ai_dialog")
                and not isinstance(mw.AnkiTerminator_image_Ai_dialog, CustomImageWidget)):
                send_imageFX_action.setEnabled(False)

        menu.addSeparator()


        # for ankiwebview inspector
        if mw.addonManager.getConfig(__name__).get("Debug", False):
            gui_hooks.webview_will_show_context_menu(self, menu)

        menu.exec(event.globalPos())

    def contextMenu(self, webview: AnkiWebView, menu: QMenu,*args,**kwargs):
        selected = webview.page().selectedText()
        if not selected:
            return
        self.parent_window.set_last_text(selected)
        # self.parent_window.more_function("random_prompt",selected)

    # def load(self, url: QUrl):
    #     request = QWebEngineHttpRequest(url)
    #     request.setHeader(b"User-Agent", b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")


class ResizableWebView(QWidget):
    def __init__(self, name, url, parent=None):
        super().__init__(parent)
        # ----------🍪 Cookie monster ---------------
        print(r"""
Cookie monster! Om nom nom nom nom nom nom...
               _  _
             _/0\/ \_
    .-.   .-` \_/\0/ '-.
   /:::\ / ,_________,  \
  /\:::/ \  '. (:::/  `'-;
  \ `-'`\ '._ `"'"'\__    \
   `'-.  \   `)-=-=(  `,   |
jgs    \  `-"`      `"-`   /
                """)
        self.cookie_profile = QWebEngineProfile("my_profile")
        # profile = QWebEngineProfile.defaultProfile() # ﾃﾞﾌｫﾙﾄのﾌﾟﾛﾌｧｲﾙ名
        self.cookie_profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        browser_storage_folder = join(dirname(__file__), USER_FILES,COOKIE_DATA)
        if not exists(browser_storage_folder):
            os.makedirs(browser_storage_folder)
        self.cookie_profile.setPersistentStoragePath(browser_storage_folder)

        # ---------- Cookie monster ---------------
        self.last_call = 0
        self.last_card = None
        self.last_text = None
        self.context_action = None
        self.loading = False
        self.last_card_note = None

        self.setWindowTitle(name)
        self.setMinimumSize(QSize(300, 300))

        self.webview = CustomWebEngineView(self)
        # self.webview = QWebEngineView()
        # self.webview = AnkiWebView()

        # ｸﾘｯﾌﾟﾎﾞｰﾄﾞにｺﾋﾟｰ可能にする
        settings = self.cookie_profile.settings() # Cookie monster
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)

        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        # auto play support
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)

        try:
            # Night Mode Support
            from aqt.theme import theme_manager
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.ForceDarkMode,
                theme_manager.get_night_mode())
        except Exception as e:
            print(e)


        # ----------------------------------
        self.grey_widget = QWidget()
        # self.grey_widget.setStyleSheet("background-color: grey;")
        addon_path = dirname(__file__)
        icon_path = join(addon_path, NOW_LOADING)
        pixmap = QPixmap(icon_path)
        self.label = QLabel(self.grey_widget)
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self.grey_widget)
        layout.addWidget(self.label)
        self.grey_widget.setLayout(layout)
        # ----------------------------------

        self.webpage = CustomWebEnginePage(self.cookie_profile, self.webview) # Cookie monster
        # self.webpage = QWebEnginePage(self.cookie_profile, self.webview) # Cookie monster
        self.webview.loadStarted.connect(self.on_load_started)
        self.webview.loadFinished.connect(self.on_load_finished)

        self.webview.loadFinished.connect(self.inject_javascript)

        # def downloadRequested(self, item): # QWebEngineDownloadItem
        #     print('downloading to', item.path())
        #     self.statusBar().showMessage("Downloading to " + item.path())
        #     item.accept()

        self.cookie_profile.downloadRequested.connect(lambda download : on_download_requested(download, self))


        self.hide_webview()

        self.webview.setPage(self.webpage)
        self.webpage.featurePermissionRequested.connect(self.on_permission_requested)

        self.webview.load(QUrl(url))

        layout = QVBoxLayout(self)
        self.last_text_toolbar(layout)
        self.make_menu_button(layout)

        layout.addWidget(self.webview)
        layout.addWidget(self.grey_widget)
        layout.setContentsMargins(1, 1, 1, 1)

        self.get_field_text()

        self.setLayout(layout)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)#たぶんいらない

        # closeEventをﾌｯｸしてｵﾌﾞｼﾞｪｸﾄを削除しないようにする
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)#たぶんいらない

        gui_hooks.webview_will_show_context_menu.remove(self.contextMenu)
        gui_hooks.webview_will_show_context_menu.append(self.contextMenu)

        gui_hooks.editor_will_show_context_menu.remove(self.contextMenu)
        gui_hooks.editor_will_show_context_menu.append(self.contextMenu)

        gui_hooks.reviewer_did_show_question.remove(self.ChatGPT_hide_webview)
        gui_hooks.reviewer_did_show_question.append(self.ChatGPT_hide_webview)

        gui_hooks.reviewer_did_show_answer.remove(self.ChatGPT_show_webview)
        gui_hooks.reviewer_did_show_answer.append(self.ChatGPT_show_webview)

        gui_hooks.reviewer_will_end.remove(self.ChatGPT_show_webview)
        gui_hooks.reviewer_will_end.append(self.ChatGPT_show_webview)

        gui_hooks.reviewer_did_show_answer.remove(self.show_answer_preload)
        gui_hooks.reviewer_did_show_answer.append(self.show_answer_preload)

        gui_hooks.reviewer_did_show_question.remove(self.show_question_preload)
        gui_hooks.reviewer_did_show_question.append(self.show_question_preload)

        self.opacity_effect_0 = QGraphicsOpacityEffect(self)
        self.opacity_effect_1 = QGraphicsOpacityEffect(self)


    def on_permission_requested(self, security_origin, feature):
        # audio support
        if feature == QWebEnginePage.Feature.MediaAudioCapture:
            self.webview.page().setFeaturePermission(
                security_origin,
                feature,
                QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )

    def remove_all_hooks(self):
        gui_hooks.webview_will_show_context_menu.remove(self.contextMenu)
        gui_hooks.editor_will_show_context_menu.remove(self.contextMenu)
        gui_hooks.reviewer_did_show_question.remove(self.ChatGPT_hide_webview)
        gui_hooks.reviewer_did_show_answer.remove(self.ChatGPT_show_webview)
        gui_hooks.reviewer_will_end.remove(self.ChatGPT_show_webview)
        gui_hooks.reviewer_did_show_answer.remove(self.show_answer_preload)
        gui_hooks.reviewer_did_show_question.remove(self.show_question_preload)


    def inject_javascript(self):
        config = mw.addonManager.getConfig(__name__)
        if config.get("now_AI_type") == OPEN_EVIDENCE:
            QTimer.singleShot(800, self._inject_oe_css)
            return
        if not config.get("now_AI_type", False) == CHAT_GPT:
            return
        if not config.get("auto_read_aloud", True):
            return

        # ｱｲﾃﾞｨｱを一部参考
        # https://github.com/3choff/ChatGPT_ReadAloud

        javascript_code = """
let clickedTestIds = new Set();

function findAndClickButton() {
    const conversationTurns = document.querySelectorAll('[data-testid^="conversation-turn-"]');
    let maxTestIdElement = null;
    let maxTestId = -1;
    conversationTurns.forEach(element => {
        const testId = parseInt(element.getAttribute('data-testid').split('-').pop());
        if (testId > maxTestId && !clickedTestIds.has(testId)) {
            maxTestId = testId;
            maxTestIdElement = element;
        }
    });

    if (maxTestIdElement) {
        const button = maxTestIdElement.querySelector('button[aria-label="More actions"]');
        if (button && !button.disabled && button.getAttribute('aria-disabled') !== 'true') {
            button.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true, cancelable: true, view: window}));
            button.dispatchEvent(new PointerEvent('pointerup', {bubbles: true, cancelable: true, view: window}));
            clickedTestIds.add(maxTestId);

            setTimeout(() => {
                const menuItem = document.querySelector('div[role="menuitem"][aria-label="Read aloud"], div[role="menuitem"][aria-label="Loading"]');
                if (menuItem) {
                    menuItem.click();
                }
            }, 500);
        }
    }
}

setInterval(findAndClickButton, 2000);
"""


        # javascript_code = """
        # let clickedTestIds = new Set();

        # function findAndClickButton() {
        #     const conversationTurns = document.querySelectorAll('[data-testid^="conversation-turn-"]');
        #     let maxTestIdElement = null;
        #     let maxTestId = -1;
        #     conversationTurns.forEach(element => {
        #         const testId = parseInt(element.getAttribute('data-testid').split('-').pop());
        #         if (testId > maxTestId && !clickedTestIds.has(testId)) {
        #             maxTestId = testId;
        #             maxTestIdElement = element;
        #         }
        #     });

        #     if (maxTestIdElement) {
        #         const button = maxTestIdElement.querySelector('span[data-state="closed"] > button[aria-label="Read aloud"]');
        #         if (button && !button.disabled && button.getAttribute('aria-disabled') !== 'true') {
        #             button.click();
        #             clickedTestIds.add(maxTestId);
        #         }
        #     }
        # }

        # setInterval(findAndClickButton, 2000);
        # """



        # javascript_code = """
        # let clickedTestIds = new Set();

        # function findAndClickButton() {
        #     const conversationTurns = document.querySelectorAll('[data-testid^="conversation-turn-"]');
        #     let maxTestIdElement = null;
        #     let maxTestId = -1;
        #     conversationTurns.forEach(element => {
        #         const testId = parseInt(element.getAttribute('data-testid').split('-').pop());
        #         if (testId > maxTestId && !clickedTestIds.has(testId)) {
        #             maxTestId = testId;
        #             maxTestIdElement = element;
        #         }
        #     });

        #     if (maxTestIdElement) {
        #         const button = maxTestIdElement.querySelector('span[data-state="closed"] > button[aria-label="Read Aloud"]');
        #         if (button && !button.disabled && button.getAttribute('aria-disabled') !== 'true') {
        #             button.click();
        #             clickedTestIds.add(maxTestId);
        #         }
        #     }
        # }

        # setInterval(findAndClickButton, 2000);
        # """

        # javascript_code = """
        # let clickedTestIds = new Set();
        # let queue = [];
        # let isPlaying = false;

        # function findAndClickButton() {
        #     const conversationTurns = document.querySelectorAll('[data-testid^="conversation-turn-"]');
        #     conversationTurns.forEach(element => {
        #         const testId = parseInt(element.getAttribute('data-testid').split('-').pop());
        #         if (!clickedTestIds.has(testId)) {
        #             const button = element.querySelector('span[data-state="closed"] > button[aria-label="Read Aloud"]');
        #             if (button && !button.disabled && button.getAttribute('aria-disabled') !== 'true') {
        #                 queue.push({ testId, button });
        #                 clickedTestIds.add(testId);
        #             }
        #         }
        #     });

        #     if (!isPlaying) {
        #         playNextInQueue();
        #     }
        # }

        # function playNextInQueue() {
        #     if (queue.length === 0) {
        #         isPlaying = false;
        #         return;
        #     }

        #     isPlaying = true;
        #     const { testId, button } = queue.shift();
        #     button.click();

        #     const intervalId = setInterval(() => {
        #         const stopButton = document.querySelector(`[data-testid="conversation-turn-${testId}"] button[aria-label="Stop"]`);
        #         if (!stopButton || stopButton.offsetParent === null) { // Check if the stop button is hidden
        #             clearInterval(intervalId);
        #             playNextInQueue();
        #         }
        #     }, 1000);
        # }

        # setInterval(findAndClickButton, 2000);
        # """

        self.webview.page().runJavaScript(javascript_code)



    def ChatGPT_hide_webview(self, *args, **kwargs):
        config = mw.addonManager.getConfig(__name__)
        hide = config["hide_the_sidebar_on_the_answer_screen"]
        if hide:
            self.change_image(SHOW_ANSWER_PNG)
            self.grey_widget.setVisible(True)
            self.webview.setVisible(False)
            self.opacity_effect_0.setOpacity(0)
            self.last_text_edit.setGraphicsEffect(self.opacity_effect_0)

            # self.webview.setFixedHeight(HIDE_HIGHT)
            # self.grey_widget.setVisible(True)
            # self.grey_widget.setFixedHeight(self.height())

    def ChatGPT_show_webview(self, *args, **kwargs):
        config = mw.addonManager.getConfig(__name__)
        hide = config["hide_the_sidebar_on_the_answer_screen"]
        if hide:
            self.grey_widget.setVisible(False)
            self.webview.setVisible(True)
            # self.last_text_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.opacity_effect_0.setOpacity(1)
            self.last_text_edit.setGraphicsEffect(self.opacity_effect_0)

            # self.grey_widget.setVisible(False)
            # self.webview.setFixedHeight(self.height())

        elif not self.loading and self.webview.height() == HIDE_HIGHT:
            self.grey_widget.setVisible(False)
            self.webview.setVisible(True)
            self.opacity_effect_0.setOpacity(1)
            self.last_text_edit.setGraphicsEffect(self.opacity_effect_0)

            # self.grey_widget.setVisible(False)
            # self.webview.setFixedHeight(self.height())
        else:
            pass

    def change_image(self, image_name):
        addon_path = dirname(__file__)
        icon_path = join(addon_path, image_name)
        pixmap = QPixmap(icon_path)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.label.setPixmap(pixmap)

    def load_url(self):
        config = mw.addonManager.getConfig(__name__)
        now_AI_type = config["now_AI_type"]
         
        if now_AI_type in config["ChatGPT_URL"]:
            ChatGPT_URL = config["ChatGPT_URL"][now_AI_type]
        elif (now_AI_type == CUSTOM_AI
            and not config["Custom_AI_URL"].isspace()):
            ChatGPT_URL = config["Custom_AI_URL"]
        else: # ﾃﾞﾌｫﾙﾄ
            ChatGPT_URL = CHAT_GPT


        self.webview.load(QUrl(ChatGPT_URL))

    def on_load_started(self):
        self.loading = True
        self.hide_webview()

    def on_load_finished(self):
        self.loading = False
        self.show_webview()

    def hide_webview(self):
        self.grey_widget.setVisible(True)
        self.webview.setVisible(False)

    def show_webview(self):
        self.grey_widget.setVisible(False)
        self.webview.setVisible(True)

    # def hide_webview(self):
    #     self.webview.setFixedHeight(HIDE_HIGHT)
    #     self.grey_widget.setVisible(True)
    #     self.grey_widget.setFixedHeight(self.height())


    # def show_webview(self):
    #     self.grey_widget.setVisible(False)
    #     self.webview.setFixedHeight(self.height())


    def last_text_toolbar(self, layout: QVBoxLayout):
        self.last_text_bar = QToolBar()
        self.last_text_bar.setStyleSheet("QToolBar { margin: 1px; padding: 1px; }")
        layout.addWidget(self.last_text_bar)

        self.make_button(
            "AI", lambda :self.change_AI_type(), self.last_text_bar, True,
            tooltip_text="Quick Change AI")

        config = mw.addonManager.getConfig(__name__)

        self.checkbox = QCheckBox()
        self.checkbox .setStyleSheet("QCheckBox { margin: 1px; padding: 1px; }")
        self.checkbox.stateChanged.connect(self.checkbox_state_changed)
        self.checkbox.setChecked(config["submit_text"])
        self.checkbox.setStyleSheet(qtip_style)
        self.checkbox.setToolTip(shige_tr.check_box_tooltip)
        self.last_text_bar.addWidget(self.checkbox)


        # auto_read_aloud ﾁｪｯｸﾎﾞｯｸｽの追加
        self.auto_read_aloud_checkbox = QCheckBox()
        self.auto_read_aloud_checkbox.setStyleSheet("QCheckBox { margin: 1px; padding: 1px; }")
        self.auto_read_aloud_checkbox.stateChanged.connect(self.auto_read_aloud_checkbox_state_changed)
        self.auto_read_aloud_checkbox.setChecked(config.get("auto_read_aloud", True))
        self.auto_read_aloud_checkbox.setStyleSheet(qtip_style)
        self.auto_read_aloud_checkbox.setToolTip("Auto-read aloud (for ChatGPT only)")
        self.last_text_bar.addWidget(self.auto_read_aloud_checkbox)
        # ------------------------------



        self.last_text_edit = QLineEdit(self.last_text)
        self.last_text_edit.setStyleSheet("QLineEdit { margin: 1px; padding: 1px; }")
        self.last_text_edit.textChanged.connect(self.update_last_text)
        self.last_text_bar.addWidget(self.last_text_edit)

        # self.make_button(shige_tr.option, self.option_button_click, self.last_text_bar)
        self.make_button(
            " ⚙️ ", self.option_button_click, self.last_text_bar,
            tooltip_text="⚙️Option")


        if True:
            self.make_button(
                "❔️", self.question_button_click, self.last_text_bar,
                tooltip_text="📖Wiki")

        config = mw.addonManager.getConfig(__name__)

        if not config.get("sidebar_rate_this_clicked", False):
            self.make_button(
                "👍️", self.rate_this_button_click, self.last_text_bar,
                tooltip_text="👍️Rate This"
                )
        else:
            self.make_button(
                "💖", self.patreon_button_click, self.last_text_bar,
                tooltip_text="💖Become a Patron"
                )

    def question_button_click(self):
        openLink("https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#ai-sidebar")

    def rate_this_button_click(self):
        ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
        if (isinstance(ADDON_PACKAGE, (int, float))
            or (isinstance(ADDON_PACKAGE, str)
            and ADDON_PACKAGE.isdigit())):
            RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"
            openLink(RATE_THIS_URL)
        config = mw.addonManager.getConfig(__name__)
        config["sidebar_rate_this_clicked"] = True
        mw.addonManager.writeConfig(__name__, config)
        PYGsound(SOUND_OPENLINK)

    def patreon_button_click(self):
        openLink("https://www.patreon.com/Shigeyuki")
        PYGsound(SOUND_OPENLINK)

    def auto_read_aloud_checkbox_state_changed(self, state):
        config = mw.addonManager.getConfig(__name__)
        config["auto_read_aloud"] = (state == 2)
        mw.addonManager.writeConfig(__name__, config)
        self.webview.reload()


    def checkbox_state_changed(self, state):
        config = mw.addonManager.getConfig(__name__)
        if state == 2:
            config["submit_text"] = True
        else:
            config["submit_text"] = False
        mw.addonManager.writeConfig(__name__, config)

    # Pretty display names for the AI picker menu
    _AI_DISPLAY_NAMES = {
        "Chat_GPT":     "ChatGPT",
        "Google_Bard":  "Google Gemini",
        "Bing_Chat":    "Bing Chat",
        "Claude":       "Claude",
        "perplexity":   "Perplexity",
        "DeepSeek":     "DeepSeek",
        "Grok_AI":      "Grok",
        "Duck_AI":      "DuckDuckGo AI",
        "Open_Evidence":"Open Evidence",
    }

    def change_AI_type(self, update=True):
        """Show a direct picker menu so the user can jump to any AI in one click."""
        config = mw.addonManager.getConfig(__name__)
        current = config.get("now_AI_type")

        menu = QMenu()
        for theme in THEMES:
            label = self._AI_DISPLAY_NAMES.get(theme, theme.replace("_", " "))
            action = QAction(label, menu)
            action.setCheckable(True)
            action.setChecked(theme == current)
            action.triggered.connect(lambda _, t=theme: self._switch_to_ai(t))
            menu.addAction(action)

        from aqt.qt import QCursor
        menu.exec(QCursor.pos())

    def _switch_to_ai(self, theme: str) -> None:
        config = mw.addonManager.getConfig(__name__)
        config["now_AI_type"] = theme
        mw.addonManager.writeConfig(__name__, config)
        PYGsound(THEME_CHANGE)
        self.load_url()
        self._rebuild_prompt_toolbar()
        from .update_top_toolbar import change_AI_icon_on_top_tool_bar
        change_AI_icon_on_top_tool_bar()


    def option_button_click(self):
        set_this_addon_Config()


    def update_last_text(self, text):
        # ﾃｷｽﾄが編集されたときにself.last_textを更新
        self.last_text = text

    def set_last_text(self, text):
        # self.last_textを更新し､ﾃｷｽﾄｴﾃﾞｨｯﾄも更新
        self.last_text = text
        self.last_text_edit.setText(text)


    def get_field_text(self, card=None):
        config = mw.addonManager.getConfig(__name__)
        if card is None and mw.state == "review":
            card = mw.reviewer.card
        else:
            return
        self.last_card = card
        note = card.note()
        self.last_card_note = note
        note_type = note.note_type()

        if self.is_excluded_note_type(config, note_type):
            return

        # field_names = note_type['flds']
        # first_field_name = field_names[0]['name']

        first_field_name = self.get_priority_field_name(config, note_type)

        text = card.note()[first_field_name]
        self.set_last_text(text)

    # def make_menu_button(self, layout: QVBoxLayout):
    #     config = mw.addonManager.getConfig(__name__)
    #     b_name = config["button_name"]

    #     # ﾎﾞﾀﾝの名前とｱｸｼｮﾝのﾘｽﾄ
    #     buttons = [
    #         # ("field", self.field_function),
    #         (b_name[0], lambda: self.more_function("random_prompt")),
    #         (b_name[1], lambda: self.more_function("more_info")),
    #         (b_name[2], lambda: self.more_function("baby_explanation")),
    #         (b_name[3], lambda: self.more_function("word_origin")),
    #         (b_name[4], lambda: self.more_function("make_joke")),
    #         (b_name[5], lambda: self.more_function("history")),
    #         (b_name[6], lambda: self.more_function("synonym")),
    #         (b_name[7], lambda: self.more_function("mnemonic")),
    #     ]

    #     # ﾂｰﾙﾊﾞｰを作成
    #     self.toolBar = QToolBar()
    #     self.toolBar.setStyleSheet("QToolBar { margin: 1px; padding: 1px; }")

    #     layout.addWidget(self.toolBar)

    #     layout.setContentsMargins(1, 1, 1, 1)

    #     for button_name, action_function in buttons:
    #         self.make_button(button_name, action_function, self.toolBar)

    # ---------------------------------------------------

    def get_button_function_pairs(self, config):
        
        b_name = config["button_name"]

        button_function_pairs = {
            "random_prompt": b_name[0],
            "more_info": b_name[1],
            "baby_explanation": b_name[2],
            "word_origin": b_name[3],
            "make_joke": b_name[4],
            "history": b_name[5],
            "synonym": b_name[6],
            "mnemonic": b_name[7]
        }
        return b_name, button_function_pairs



    def make_menu_button(self, layout: QVBoxLayout):
        self.toolBar = QToolBar()
        self.toolBar.setStyleSheet("QToolBar { margin: 1px; padding: 1px; }")
        layout.addWidget(self.toolBar)
        layout.setContentsMargins(1, 1, 1, 1)
        self._rebuild_prompt_toolbar()


    # ｺﾝﾎﾞﾎﾞｯｸｽ ========================
    def save_selection(self):
        if not self.combo_box:
            return
        selected_key = self.combo_box.currentData()
        config = mw.addonManager.getConfig(__name__)
        config["default_prompt"] = selected_key
        mw.addonManager.writeConfig(__name__, config)

    def adjust_combo_box_width(self):
        if not self.combo_box:
            return
        font_metrics = QFontMetrics(self.combo_box.font())
        text = self.combo_box.currentText()
        width = font_metrics.horizontalAdvance(text) + 40  # 余白を追加
        self.combo_box.setFixedWidth(width)

    def make_combo_box(self, button_function_pairs):
        config = mw.addonManager.getConfig(__name__)
        default_prompt = config.get("default_prompt", "random_prompt")
        self.combo_box = QComboBox()

        for key, value in button_function_pairs.items():
            self.combo_box.addItem(value, key)

        if default_prompt not in button_function_pairs:
            default_prompt = "random_prompt"

        default_index = self.combo_box.findData(default_prompt)
        if default_index != -1:
            self.combo_box.setCurrentIndex(default_index)

        self.combo_box.currentIndexChanged.connect(self.save_selection)
        self.combo_box.currentIndexChanged.connect(self.adjust_combo_box_width)
        self.adjust_combo_box_width()
        self.toolBar.addWidget(self.combo_box)
    # ｺﾝﾎﾞﾎﾞｯｸｽ ========================

    def make_button(self, button_name, action_function, toolbar:QToolBar, sound=False, tooltip_text=None):
        action = QAction(button_name, self)
        button = QPushButton(button_name)
        fm = QFontMetrics(button.font())
        width = fm.horizontalAdvance(button_name)
        button.setFixedSize(width + 10, 25)
        # button.setStyleSheet("QPushButton { margin: 1px; padding: 1px; }")
        action.triggered.connect(action_function)
        button.clicked.connect(action.trigger)
        if sound is False:
            button.clicked.connect(lambda: PYGsound(SOUND_SELECT))

         
        custom_style_sheet = "QPushButton { margin: 1px; padding: 1px; }"
        if tooltip_text:
            button.setToolTip(tooltip_text)
            custom_style_sheet += qtip_style

        button.setStyleSheet(custom_style_sheet)
        toolbar.addWidget(button)

    # def make_button(self, button_name, action_function, toolbar, sound=False):
    #     action = QAction(button_name, self)
    #     button = QPushButton(button_name)
    #     fm = QFontMetrics(button.font())
    #     width = fm.horizontalAdvance(button_name)
    #     button.setFixedSize(width + 10, 25)
    #     button.setStyleSheet("QPushButton { margin: 1px; padding: 1px; }")
    #     action.triggered.connect(action_function)
    #     button.clicked.connect(action.trigger)
    #     if sound is False:
    #         button.clicked.connect(lambda: PYGsound(SOUND_SELECT))
    #     toolbar.addWidget(button)

    def update_button_names(self):
        # 最新の設定を取得
        config = mw.addonManager.getConfig(__name__)
        b_name, button_function_pairs = self.get_button_function_pairs(config)

        # ﾎﾞﾀﾝの名前を更新
        # for i, action in enumerate(self.toolBar.actions()):

        i = 0
        for action in self.toolBar.actions():
            button = self.toolBar.widgetForAction(action)
            if isinstance(button, QComboBox):
                self.toolBar.removeAction(action)
                self.make_combo_box(button_function_pairs)
                continue

            action.setText(b_name[i])
            button = self.toolBar.widgetForAction(action)
            button.setText(b_name[i])
            fm = QFontMetrics(button.font())
            width = fm.horizontalAdvance(b_name[i])
            button.setFixedSize(width + 10, 25)
            i += 1
    # ---------------------------------------------------

    def field_function(self):# 使ってない
        # self.load_and_interact()
        self.get_field_text()

    # def more_function(self,text,search_text=None):
    #     if search_text is not None:
    #         self.set_last_text(search_text)
    #     if self.last_text is not None:
    #         config = mw.addonManager.getConfig(__name__)
    #         more_info = config[text]
    #         more_info = random.choice(more_info)
    #         if "{}" in more_info:
    #             prompt_text = more_info.format(SYMBOL[CHOICE_SYMBOL][0]
    #                                             + self.last_text
    #                                             + SYMBOL[CHOICE_SYMBOL][1])
    #         else:
    #             prompt_text = self.last_text + more_info
    #         self.handle_load_finished(text=prompt_text, click=True)

    def more_function(self, set_text, search_text=None):
        if search_text is not None: # ﾃｷｽﾄがすでに指定されている場合
            self.set_last_text(search_text)

            if (hasattr(mw, 'reviewer') and hasattr(mw.reviewer, 'card')
                and hasattr(mw.reviewer.card, 'note')):
                self.last_card_note = mw.reviewer.card.note() # ﾚﾋﾞｭﾜｰから取得

        if self.last_text is not None:
            config = mw.addonManager.getConfig(__name__)
            more_info = config[set_text]
            more_info = random.choice(more_info)
            if "{}" in more_info:
                prompt_text = more_info.format(SYMBOL[CHOICE_SYMBOL][0]
                                                + self.last_text
                                                + SYMBOL[CHOICE_SYMBOL][1])
            else:
                prompt_text = self.last_text + more_info
            self.handle_load_finished(prompt_text=prompt_text, click=True)


    def wrap_with_quotes(self,text):
        return "'" + text + "'"


    def explain_with_ankiteminator(self, selected):
        print(selected)
        if not selected:
            return
        config = mw.addonManager.getConfig(__name__)
        default_prompt = config.get("default_prompt", "random_prompt")
        if default_prompt not in config:
            default_prompt = "random_prompt"
        self.more_function(default_prompt, selected)
        print("done")

    def contextMenu(self, webview: AnkiWebView, menu: QMenu,*args,**kwargs):
        selected = webview.page().selectedText()
        if not selected:
            return
        menu.addSeparator()
        self.context_action = QAction("🤖Explain with AnkiTerminator", mw)

        # config = mw.addonManager.getConfig(__name__)
        # default_prompt = config.get("default_prompt", "random_prompt")
        # if default_prompt not in config:
        #     default_prompt = "random_prompt"

        # self.context_action.triggered.connect(lambda default_prompt=default_prompt, selected=selected: self.more_function(default_prompt, selected))

        self.context_action.triggered.connect(lambda _, selected=selected: self.explain_with_ankiteminator(selected))

        menu.addAction(self.context_action)

    def show_answer_preload(self,card:Card=None,*args,**kwargs):
        config = mw.addonManager.getConfig(__name__)
        hide = config["hide_the_sidebar_on_the_answer_screen"]
        submit = config["submit_text"]
        if not hide or not submit:
            self.load_and_interact(card,*args,**kwargs)

    def show_question_preload(self,card:Card=None,*args,**kwargs):
        config = mw.addonManager.getConfig(__name__)
        hide = config["hide_the_sidebar_on_the_answer_screen"]
        submit = config["submit_text"]
        if hide and submit:
            self.load_and_interact(card,*args,**kwargs)


    def load_and_interact(self,card:Card=None,*args,**kwargs):
        # ﾄﾞｯｸﾞが非表示にされていたらGuiHooksを実行しない
        if not self.isVisible():
            return

        # 特定のﾉｰﾄﾀｲﾌﾟで2回呼び出される場合があるので1秒に制限
        current_time = time.time()
        if current_time - self.last_call < 1:
            return
        self.last_call = current_time

        config = mw.addonManager.getConfig(__name__)

        # text = mw.reviewer.card.note()["Front"] + selected_prompt

        if card is None and self.last_card is not None:# 手動で2回目の呼び出し
            card = self.last_card
        if card is None and self.last_card is None:
            return
        self.last_card = card
        note = card.note()
        self.last_card_note = note
        note_type = note.note_type()

        # 特定のﾉｰﾄﾀｲﾌﾟを除外
        if self.is_excluded_note_type(config, note_type):
            return

        # OE mode: build a medical query and inject it via OE's JS method
        if config.get("now_AI_type") == OPEN_EVIDENCE:
            card_text = _oe_extract_card_text(card)
            self.set_last_text(card_text)
            query = OE_PRESETS[0]["template"].format(card_text) + _OE_SUFFIX
            self.handle_load_finished(query)
            return

        first_field_name = self.get_priority_field_name(config, note_type)

        default_prompt = config.get("default_prompt", "random_prompt")
        if default_prompt not in config:
            default_prompt = "random_prompt"
        random_prompt = config[default_prompt]

        # random_prompt = config["random_prompt"]
        selected_prompt = random.choice(random_prompt)


        note_field_text = card.note()[first_field_name]
        self.set_last_text(note_field_text)
        if "{}" in selected_prompt:
            prompt_text = selected_prompt.format(SYMBOL[CHOICE_SYMBOL][0]
                                                    + note_field_text +
                                                    SYMBOL[CHOICE_SYMBOL][1])
        else:
            prompt_text = note_field_text + selected_prompt
        self.handle_load_finished(prompt_text)

    # ------------------------------------------------

     
    def is_excluded_note_type(self, config, note_type):
        exclusion_list = config["exclusion_list"]
        # 特定のﾉｰﾄﾀｲﾌﾟを除外
        note_type_name = note_type['name']
        for exclusion in exclusion_list:
            if not exclusion or exclusion.isspace():
                continue
            if exclusion in note_type_name:
                return True
        return False

    def get_priority_field_name(self, config, note_type):
        Priority_Fields_list = config["Priority_Fields_list"]
        field_names = note_type['flds']
        first_field_name = field_names[0]['name']
        for field in field_names:
            if field['name'] in Priority_Fields_list:
                first_field_name = field['name']
                break
        return first_field_name

    def get_priority_tag(self, config):
        Priority_tag_list = config["Priority_tag_list"]
        if self.last_card_note is not None:
            note = self.last_card_note # 引数から直接でないとｽﾞﾚるかも知らん
            tags = note.tags
            priority_tag = ""
            for tag in tags:
                for priority_tag_item in Priority_tag_list:
                    if priority_tag_item in tag:
                        priority_tag = priority_tag_item
                        break
                if priority_tag:
                    break
            return priority_tag
        else:
            priority_tag = ""

    # ------------------------------------------------

    # 送信ﾎﾞﾀﾝを押しても実行されないのでこれを参考にした
    # https://stackoverflow.com/questions/57879322/how-can-i-enter-data-into-a-custom-handled-input-field/57900849#57900849
            # BingChatはﾃｷｽﾄの入力すらもできません¯\_(ﾂ)_/¯
            # URLでｱｸｾｽすればいけるかも知らん(でもﾛｰﾄﾞが長い)

    ### clip bord ###
    def restore_clipboard(self):
        if isinstance(self.original_clipboard_data, QMimeData):
            self.clipboard.clear()
            self.clipboard.setMimeData(self.original_clipboard_data, QClipboard.Mode.Clipboard)
            self.original_clipboard_data = None

    def paste_from_clipboard(self):
        print("> run paste_from_clipboard")
        if self.auto_send_prompt_text:
            if self.auto_send_prompt_text == self.clipboard.text():
                self.webview.triggerPageAction(QWebEnginePage.WebAction.Paste)
                self.auto_send_prompt_text = None
                print("> paste done")
            else:
                print("!None prompt")

    def webaction_select_all(self):
        print("> run paste_from_clipboard")
        if self.auto_send_prompt_text:
            if self.auto_send_prompt_text == self.clipboard.text():
                self.webview.triggerPageAction(QWebEnginePage.WebAction.SelectAll)
                print("> SelectAll")



    ### send prompt ###
    def handle_load_finished(self, prompt_text:str, click=False):
        config = mw.addonManager.getConfig(__name__)

        # if not config["input_text"] :
        if not (config["submit_text"] or click):
            return

        # OE uses its own React-compatible injection — bypass all other AI logic
        if config.get("now_AI_type") == OPEN_EVIDENCE:
            QTimer.singleShot(600, lambda: self._oe_inject_query(prompt_text))
            return

        no_auto_press_send_button = config.get("no_auto_press_send_button", False)

        if config["change_Language"]:
            random_prompt_lang = config["language"]
            selected_prompt_lang = random.choice(random_prompt_lang)
            lang = shige_tr.lang
            print(lang)
            # if '{}' in selected_prompt_lang and lang is not None:
            if '{}' in selected_prompt_lang:
                selected_prompt_lang = selected_prompt_lang.replace('{}', lang if lang else "")
            prompt_text  = prompt_text + " " + selected_prompt_lang

        if config["is_i_am_studying"]:
            random_i_am_studying = config["i_am_studying"]
            selected_prompt_study = random.choice(random_i_am_studying)
            study_tag = self.get_priority_tag(config)
            # if '{}' in selected_prompt_study and study_tag is not None:
            if '{}' in selected_prompt_study:
                selected_prompt_study = selected_prompt_study.replace('{}', study_tag if study_tag else "")
            prompt_text  = selected_prompt_study + " " + prompt_text

        now_AI_type = config["now_AI_type"]


        #📍use V2
        list_use_auto_prompt_v2 = [GOOGLE_BARD, BING_CHAT, PERPLEXITY]


        if not now_AI_type in list_use_auto_prompt_v2:
            prompt_text = prompt_text.replace("'", "\\'")
            prompt_text = prompt_text.replace('"', '\\"')
            prompt_text = prompt_text.replace('\n', '\\n')
            prompt_text = prompt_text.replace('\r', '\\n')

        # skip_response_icon_check = "true"

        parent_element = ""
        if now_AI_type == CHAT_GPT:
            class_name = "#prompt-textarea"
            button_class = 'button[data-testid="send-button"]'
            # button_class = 'button[data-testid="fruitjuice-send-button"]'
            # stop_button_class = 'button[aria-label="Stop generating"]'
            stop_button_class = 'button[data-testid="stop-button"]'
            # stop_button_class = 'button[data-testid="fruitjuice-stop-button"]'
            parent_element = ""

        elif now_AI_type == GROK_AI: #🚀
            # class_name = 'textarea[name="query"]'  #".c92459f0"
            # class_name = "textarea.min-h-14"  #".c92459f0"
            class_name = '.tiptap.ProseMirror' #".query-bar textarea"
            button_class = 'button[type="submit"]' #'.f6d670'
            stop_button_class = 'button[type="submit"]' #''.f6d670' #'.f286936b'
            parent_element = ""

        elif now_AI_type == DUCK_AI: #🦆
            class_name = 'textarea[name="user-prompt"]'
            button_class = 'button[type="submit"].OBhZtIxa9q5aVP29xT9j'
            stop_button_class = 'button[type="submit"].YwVAQQko8KMb8FFwqGMD'
            parent_element = ""

        elif now_AI_type == DEEP_SEEK: #🐋
            class_name = "textarea._27c9245" #"#chat-input" #".c92459f0"
            button_class = '._52c986b' #'._7436101' #'._17e543b._7436101' #'._6f28693' #'.f6d670'
            stop_button_class = '' #'._17e543b._7436101'  #'._6f28693' #''.f6d670' #'.f286936b'
            stop_button_class = ''
            parent_element = ""

        elif now_AI_type == PERPLEXITY:
            # class_name = '.grow.block textarea'#"textarea.caret-superDuper"
            class_name = "#ask-input"
            button_class = 'button[aria-label="Submit"]'
            stop_button_class = ""#'button.bg-offsetPlus'
            parent_element = ""

        elif now_AI_type == CLAUDE:
            class_name = '.ProseMirror'
            button_class = 'button[aria-label="Send message"]' #'button[aria-label="Send Message"]'
            stop_button_class = 'button[aria-label="Stop response"]'#'button[aria-label="Stop Response"]'
            parent_element = ""

        elif now_AI_type == IMAGE_FX:
            class_name = '[role="textbox"]'
            button_class = '.sc-6eb6c34b-1'
            stop_button_class = ''
            parent_element = ""

        elif now_AI_type == GOOGLE_BARD:
            class_name = ".textarea.new-input-ui"#".ql-editor.textarea"
            button_class = '.send-button.submit'#".send-button"
            stop_button_class = '.send-button.stop'#".send-button"
            parent_element = ""

            # stop_button_class = "span.overline"
            # parent_element = ".parentElement"
            # skip_response_icon_check = "document.querySelector('svg[alt=\"skip response icon\"]')"

        elif now_AI_type == BING_CHAT:
            class_name = "#userInput"
            # button_class = ".rounded-submitButton"
            button_class = '[data-testid="submit-button"]'
            stop_button_class = ""


            # if config["submit_text"] or click :
            # encoded_text = urllib.parse.quote(prompt_text)
            # url = f"https://www.bing.com/search?showconv=1&sendquery=1&q={encoded_text}"
            # self.webview.load(QUrl(url))

            # return


        else:
            return


        


        #https://github.com/shigeyukey/Anki-Terminator-/issues/25
        # js_code = f"""
        # function replaceValue(selector, value) {{
        #     const el = document.querySelector(selector);
        #     if (el) {{
        #         el.focus();

        #         while (el.firstChild) {{
        #             el.removeChild(el.firstChild); // Remove existing text
        #         }}

        #         const textNode = document.createTextNode(value);
        #         el.appendChild(textNode); // Add new text

        #         const range = document.createRange();
        #         range.selectNodeContents(el);
        #         range.collapse(false);
        #         const selection = window.getSelection();
        #         selection.removeAllRanges();
        #         selection.addRange(range); // Place cursor at the end

        #         el.dispatchEvent(new Event('input', {{bubbles: true}}));
        #         el.dispatchEvent(new Event('change', {{bubbles: true}})); // Trigger events
        #     }}
        #     return el;
        # }}
        # replaceValue('{class_name}', '{text}');
        # """

        if no_auto_press_send_button:
            stop_button_class = ""
            button_class = ""



        if now_AI_type in list_use_auto_prompt_v2:

            if stop_button_class:
                js_code = f"""
                function clickButton() {{
                    var button = document.querySelector('{stop_button_class}');
                    if (button && !button.disabled && button.getAttribute('aria-disabled') !== 'true') {{
                        button.click();
                    }}
                }}
                clickButton();
                """
                self.webview.page().runJavaScript(js_code, self.js_callback)

            # js_code = f"""
            # function focusAndSelectElement(selector) {{
            #     const el = document.querySelector(selector);
            #     if (el) {{
            #         el.focus();
            #         if (el.select) {{
            #             el.select();
            #         }}
            #         el.click();
            #     }}
            #     return el;
            # }}
            # setTimeout(function() {{
            #     focusAndSelectElement('{class_name}');
            # }}, 100);
            # """


            js_code = f"""
            function focusAndSelectElement(selector) {{
                const el = document.querySelector(selector);
                if (el) {{
                    el.focus();
                    if (el.select) {{
                        el.select();
                    }}
                    el.dispatchEvent(new PointerEvent('pointerdown', {{bubbles: true, cancelable: true, view: window}}));
                    el.dispatchEvent(new PointerEvent('pointerup', {{bubbles: true, cancelable: true, view: window}}));
                    el.dispatchEvent(new MouseEvent('click', {{bubbles: true, cancelable: true, view: window}}));
                }}
                return el;
            }}
            setTimeout(function() {{
                focusAndSelectElement('{class_name}');
            }}, 100);
            """


            self.clipboard = mw.app.clipboard()
            original_data = self.clipboard.mimeData(QClipboard.Mode.Clipboard)
            self.original_clipboard_data = QMimeData()
            for format in original_data.formats():
                # print(" - format:", format)
                self.original_clipboard_data.setData(format, original_data.data(format))

            # self.webview.page().runJavaScript(js_code, self.js_callback)
            print("prompt_text:", prompt_text)
            self.clipboard.clear()
            self.clipboard.setText(prompt_text)
            self.auto_send_prompt_text = prompt_text
            QTimer.singleShot(400, self.webaction_select_all)
            QTimer.singleShot(500, self.paste_from_clipboard)


            if button_class:
                js_code += f"""
            setTimeout(function() {{
                var submitButton = document.querySelector('{button_class}');
                if (submitButton && !submitButton.disabled && submitButton.getAttribute('aria-disabled') !== 'true') {{
                    submitButton.click();
                }}
            }}, 600);
            """

            self.webview.page().runJavaScript(js_code, self.js_callback)

            QTimer.singleShot(700, self.restore_clipboard)
            return


        js_code = f"""

        function replaceValue(selector, value) {{
        const el = document.querySelector(selector);
        if (el) {{
            el.focus();
            document.execCommand('selectAll');
            if (!document.execCommand('insertText', false, value)) {{
            el.value = '{prompt_text}';
            }}
            el.dispatchEvent(new Event('change', {{bubbles: true}}));
            var inputEvent = new Event('input', {{ bubbles: true, cancelable: true }});
            el.dispatchEvent(inputEvent);
        }}
        return el;
        }}
        replaceValue('{class_name}', '{prompt_text}');
        """

        if stop_button_class:
            js_code += f"""
            setTimeout(function() {{
                var button = document.querySelector('{stop_button_class}'){parent_element};
                if (button) {{
                    button.click();
                }}
            }}, 100);
            """

        # js_code += f"""
        # setTimeout(function() {{
        #     if ({skip_response_icon_check}) {{
        #         var button = document.querySelector('{stop_button_class}'){parent_element};
        #         if (button && !button.disabled && button.getAttribute('aria-disabled') !== 'true') {{
        #             button.click();
        #         }}
        #     }}
        # }}, 100);
        # """

        # if config["submit_text"] or click:
        if button_class:
            js_code += f"""
        setTimeout(function() {{
            var submitButton = document.querySelector('{button_class}');
            if (submitButton && !submitButton.disabled && submitButton.getAttribute('aria-disabled') !== 'true') {{
                submitButton.click();
            }}
        }}, 200);
        """

        # if config["submit_text"] or click :
        #     js_code += f"""
        #     setTimeout(function() {{
        #         var submitButton = document.querySelector('{button_class}');
        #         if (submitButton) {{
        #             submitButton.click();
        #         }}
        #     }}, 200);
        #     """

        self.webview.page().runJavaScript(js_code, self.js_callback)


    def js_callback(self, result):
        print("JavaScript result: ", result)

    # ── Open Evidence helpers ─────────────────────────────────────────────────

    def _oe_inject_query(self, query: str) -> None:
        escaped = (
            query
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "")
        )
        js = _OE_INJECT_JS.replace("OE_QUERY_PLACEHOLDER", f'"{escaped}"')
        self.webview.page().runJavaScript(js)

    def _inject_oe_css(self) -> None:
        css = (
            "header { display: none !important; }"
            "body { padding-top: 0 !important; margin-top: 0 !important; }"
            "main, [class*='main'], [class*='content'] "
            "{ margin-top: 0 !important; padding-top: 0 !important; }"
        )
        js = f"""
        (function() {{
            var s = document.createElement('style');
            s.id = 'oe-hide-header';
            s.textContent = {repr(css)};
            var target = document.head || document.documentElement;
            if (target && !document.getElementById('oe-hide-header')) {{
                target.appendChild(s);
            }}
        }})();
        """
        self.webview.page().runJavaScript(js)

    def _rebuild_prompt_toolbar(self) -> None:
        config = mw.addonManager.getConfig(__name__)
        self.toolBar.clear()
        self.combo_box = None
        b_name, button_function_pairs = self.get_button_function_pairs(config)
        self.make_combo_box(button_function_pairs)
        buttons = [
            (b_name[0], lambda: self.more_function("random_prompt")),
            (b_name[1], lambda: self.more_function("more_info")),
            (b_name[2], lambda: self.more_function("baby_explanation")),
            (b_name[3], lambda: self.more_function("word_origin")),
            (b_name[4], lambda: self.more_function("make_joke")),
            (b_name[5], lambda: self.more_function("history")),
            (b_name[6], lambda: self.more_function("synonym")),
            (b_name[7], lambda: self.more_function("mnemonic")),
        ]
        for button_name, action_function in buttons:
            self.make_button(button_name, action_function, self.toolBar)

    # ─────────────────────────────────────────────────────────────────────────






chatGPTdockWidget = None #type: QDockWidget
dock_content = None #type: ResizableWebView


def check_dock_widget_position():
    if not isinstance(chatGPTdockWidget, QDockWidget):
        return
    dock_widgets = mw.findChildren(QDockWidget)
    widget_found = False
    for widget in dock_widgets:
        if widget.objectName() == "AnkiTerminator_dock":
            widget_found = True
            current_area = mw.dockWidgetArea(widget)
            if current_area != Qt.DockWidgetArea.RightDockWidgetArea:
                mw.removeDockWidget(widget)
                mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, widget)
            break
    if not widget_found:
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, chatGPTdockWidget)


def Web_view(name, url):
    global chatGPTdockWidget
    global dock_content
    global web_shortcut

    if chatGPTdockWidget is not None:
        if chatGPTdockWidget.isVisible():
            chatGPTdockWidget.hide()
            mw.web.setFocus()
        else:
            chatGPTdockWidget.show()
            chatGPTdockWidget.setFocus()
            check_dock_widget_position()
            dock_content.get_field_text()
        return

    # dock_content = ResizableWebView(name, url, mw)
    # chatGPTdockWidget = QDockWidget(mw)

    mw.anki_Terminator_dock_content = dock_content = ResizableWebView(name, url)
    mw.anki_Terminator_chatGPTdockWidget = chatGPTdockWidget = QDockWidget()

    # if mw.addonManager.getConfig(__name__).get("Debug", False):
    #     mw.anki_Terminator_02_webview = ResizableWebView(name, url)
    #     mw.anki_Terminator_02_widget = QDockWidget()
    #     mw.anki_Terminator_02_widget.setWidget(mw.anki_Terminator_02_webview)
    #     mw.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, mw.anki_Terminator_02_widget)

    # if not mw.addonManager.getConfig(__name__).get("Debug", False):
    chatGPTdockWidget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    chatGPTdockWidget.setTitleBarWidget(QWidget()) # ﾀｲﾄﾙﾊﾞｰを空のｳｨｼﾞｪｯﾄに置き換え

    chatGPTdockWidget.setObjectName("AnkiTerminator_dock")
    # chatGPTdockWidget.setWindowTitle("AnkiTerminator")
    chatGPTdockWidget.setWidget(dock_content)
    QTimer.singleShot(0, lambda: mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, chatGPTdockWidget))

    # mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, chatGPTdockWidget)

    QTimer.singleShot(500, check_dock_widget_position)

    config = mw.addonManager.getConfig(__name__)
    Enter_Short_cut_Key = config["Enter_Short_cut_Key"]

    # web_shortcut = QShortcut(QKeySequence(Enter_Short_cut_Key), dock_content)
    # web_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

    # def execute_current_item():
    #     # JavaScriptを使用して､現在選択されている項目を取得し､その項目を実行
    #     dock_content.webview.page().runJavaScript("""
    #         var activeElement = document.activeElement;
    #         if (activeElement) {
    #             activeElement.click();
    #         }
    #     """)
    # web_shortcut.activated.connect(execute_current_item)

    def send_shortcut():
        print("send_shortcut")
        config = mw.addonManager.getConfig(__name__)
        now_AI_type = config["now_AI_type"]
        if now_AI_type == CHAT_GPT:
            button_class = 'button[data-testid="send-button"]'
        elif now_AI_type == GOOGLE_BARD:
            button_class = ".send-button"
        else:
            return
        js_code = f"""
        setTimeout(function() {{
            var submitButton = document.querySelector('{button_class}');
            if (submitButton) {{
                submitButton.click();
            }}
        }}, 200);
        """
        dock_content.webview.page().runJavaScript(js_code, dock_content.js_callback)
    # web_shortcut.activated.connect(send_shortcut)

    # menu = QAction(name, mw)
    menu = QAction("Send Prompt", mw)
    menu.triggered.connect(send_shortcut)

    from .make_manu import get_anki_terminator_menu
    get_anki_terminator_menu().addAction(menu)
    # mw.form.menuTools.addAction(menu)

    menu.setShortcut(QKeySequence(Enter_Short_cut_Key))
    web_shortcut = menu

    make_close_menu_action()


def make_close_menu_action():
    global completely_close_sidebar
    completely_close_sidebar = QAction("Completely close Sidebar (for update add-on)", mw)
    completely_close_sidebar.triggered.connect(close_all_dock_widget)
    from .make_manu import get_anki_terminator_menu
    get_anki_terminator_menu().addAction(completely_close_sidebar)


# add-onを更新するときにｻｲﾄﾞﾊﾞｰを閉じる関数 ======

def close_all_dock_widget(*args, **kwargs):
    # print(mw.pm.meta["last_addon_update_check"])
    # mw.pm.meta["last_addon_update_check"] = 1722384000
    # 1735544538
    # mw.pm.meta["last_addon_update_check"] = 1722384000
    global chatGPTdockWidget
    global dock_content
    global web_shortcut
    global completely_close_sidebar

    if isinstance(chatGPTdockWidget, QDockWidget):
        if isinstance(dock_content, ResizableWebView):
            dock_content.remove_all_hooks()
            dock_content.close()
            dock_content.deleteLater()
            dock_content = None

        chatGPTdockWidget.close()
        chatGPTdockWidget.deleteLater()
        chatGPTdockWidget = None

    if hasattr(mw, "AnkiTerminator_image_Ai_dialog"):
        AI_image_widet = mw.AnkiTerminator_image_Ai_dialog
        if isinstance(AI_image_widet, QWidget):
            AI_image_widet.close()
            AI_image_widet.deleteLater()
            mw.AnkiTerminator_image_Ai_dialog = None

    from .make_manu import get_anki_terminator_menu

    if web_shortcut:
        get_anki_terminator_menu().removeAction(web_shortcut)
        web_shortcut = None

    if completely_close_sidebar:
        get_anki_terminator_menu().removeAction(completely_close_sidebar)
        completely_close_sidebar = None

gui_hooks.addons_dialog_will_show.append(close_all_dock_widget)

    # print(mw.pm.meta["last_addon_update_check"])
    # print(mw.pm.meta)
    # mw.pm.meta["last_addon_update_check"] = 1722384000
    # print(mw.pm.meta["last_addon_update_check"])
    # print(mw.pm.meta)

# 1735544538
# {'ver': 0, 'updates': True, 'created': 1639656151, 'id': 4428824829328961616, 'lastMsg': -1, 'suppressUpdate': '23.12.1', 'firstRun': False, 'defaultLang': 'en_US', 'last_addon_update_check': 1735544538, 'night_mode': False, 'uiScale': 1.0, 'last_run_version': 240603, 'new_import_export': False, 'theme': 2, 'last_loaded_profile_name': '00_shigeyukey', 'reduced_motion': False, 'legacy_import': False, 'browser_layout': 'horizontal', 'currentTagsCollapsed': False, 'addTagsCollapsed': True, 'browserTagsCollapsed': True, 'reduce_motion': 0, 'hide_bottom_bar': 0, 'bottom_bar_hide_mode': 1, 'minimalist_mode': 0, 'hide_top_bar': 0, 'top_bar_hide_mode': 1, 'widget_style': 0, 'spacebar_rates_card': 2, 'answer_keys': {1: '1', 2: '2', 3: '3', 4: '4'}, 'amboss': {'greeting_onboarding_v1_shown': True}}


try:
    from anki.hooks import wrap
    from aqt.addons import ChooseAddonsToUpdateDialog

    def addons_to_update_dialog_did_show(*args, **kawargs):
        close_all_dock_widget()
        print(f"[{ADDON_NAME}] >>> on close_all_dock_widget")

    ChooseAddonsToUpdateDialog.ask = wrap(ChooseAddonsToUpdateDialog.ask, addons_to_update_dialog_did_show)
except:
    pass



#📍beta, not tested ----------------
# try:
#     from anki.hooks import wrap
#     # from aqt.addons import ChooseAddonsToUpdateDialog
#     from aqt import addons

#     # def addons_to_update_dialog_did_show(*args, **kawargs):
#     #     # close_all_dock_widget()
#     #     QTimer.singleShot(0, close_all_dock_widget)
#     #     print(f"[{ADDON_NAME}] > run close_all_dock_widget")
#     # ChooseAddonsToUpdateDialog.ask = wrap(ChooseAddonsToUpdateDialog.ask, addons_to_update_dialog_did_show)

#     def addons_to_update_dialog_did_show(
#             parent,
#             mgr,
#             updated_addons,
#             on_done,
#             requested_by_user,
#             *args, **kawargs):
#         try:
#             if not requested_by_user:
#                 prompt_update = False
#                 for addon in updated_addons:
#                     if mgr.addon_meta(str(addon.id)).update_enabled:
#                         prompt_update = True
#                 if not prompt_update:
#                     return

#             # close_all_dock_widget()
#             QTimer.singleShot(0, close_all_dock_widget)
#             print(f"[{ADDON_NAME}] maybe update, close all dock.")

#         except Exception as e:
#             print(f"[{ADDON_NAME}] Error: {e}")

#     addons.prompt_to_update = wrap(
#         old=addons.prompt_to_update,
#         new=addons_to_update_dialog_did_show,
#         pos="before",
#     )
# except:
#     pass
#--------------------------------------









# =========================================

# from aqt.main import AnkiQt,Callable,DownloadLogEntry,DownloadLogEntry,int_time,check_and_prompt_for_updates
# from anki.hooks import wrap
# import time

# def check_for_addon_updates(
#     self,
#     by_user: bool,
#     on_done: Callable[[list[DownloadLogEntry]], None] | None = None,
# ) -> None:
#     def wrap_on_updates_installed(log: list[DownloadLogEntry]) -> None:
#         self.on_updates_installed(log)
#         self.pm.set_last_addon_update_check(int_time())
#         if on_done:
#             on_done(log)

#     check_and_prompt_for_updates(
#         self,
#         self.addonManager,
#         wrap_on_updates_installed,
#         requested_by_user=by_user,
#     )


# def addons_to_update_dialog_did_show(*args, **kawargs):
#     close_all_dock_widget()

# AnkiQt.check_for_addon_updates = wrap(AnkiQt.check_for_addon_updates, check_for_addon_updates, "around")





from .config.BGM_player import pyg_play_sound

def get_path(name):
    addon_path = dirname(__file__)
    parentFoldere = SOUND_SYSTEM
    config_folder = CONFIG_FOLDER
    audio_folder = join(addon_path,config_folder,parentFoldere, name)
    return audio_folder

def PYGsound(sound_name,volume=None):
    config = mw.addonManager.getConfig(__name__)
    if not volume == None:
        EffectVolume = volume
    else:
        EffectVolume = config["EffectVolume"]
    pyg_play_sound(get_path(sound_name), EffectVolume,False,True)





# from aqt.utils import tooltip
# def close_dock_widget(addonmanager, name, *args, **kwargs):
#     if name == __name__.split(".")[0]:
#         global chatGPTdockWidget
#         global dock_content
#         global web_shortcut
#         if isinstance(chatGPTdockWidget, QDockWidget):
#             tooltip("")

# gui_hooks.addon_manager_did_install_addon.append(close_dock_widget)
# gui_hooks.addons_dialog_will_delete_addons.append(close_dock_widget)
# gui_hooks.addons_dialog_will_delete_addons.append(close_dock_widget)


# 🚨 add-onの更新時にAnkiがｸﾗｯｼｭするﾊﾞｸﾞがある
    # def close_cookie_profile(self):

    #     if hasattr(self, 'webview'):
    #         if self.webview.page():
    #             page = self.webview.page()
    #             self.webview.setPage(None)
    #             page.deleteLater()
    #             # del page
    #         # del self.webview
    #         self.webview.deleteLater()
    #         self.webview = None

    #     if hasattr(self, 'webpage'):
    #         # del self.webpage
    #         self.webpage.deleteLater()
    #         self.webpage = None

    #     QCoreApplication.processEvents()

    #     self.cookie_profile.setPersistentStoragePath("")
    #     self.cookie_profile.setPersistentCookiesPolicy(
    #         QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)

    #     referrers = gc.get_referrers(self.cookie_profile)
    #     if len(referrers) == 1:  # 参照がselfのみ
    #         # deleteLaterだと削除されない
    #         # webviewが削除されるにdelするとｸﾗｯｼｭする
    #         del self.cookie_profile
    #         self.cookie_profile = None


# 🚨 add-onの更新時にAnkiがｸﾗｯｼｭするﾊﾞｸﾞがある
# def close_dock_widget(addonmanager, name, *args, **kwargs):
#     if name == __name__.split(".")[0]:

#         def delayed_close():
#             global chatGPTdockWidget
#             global dock_content
#             if isinstance(chatGPTdockWidget, QDockWidget):
#                 if isinstance(dock_content, ResizableWebView):
#                     dock_content.close_cookie_profile()
#                     dock_content.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
#                     dock_content.close()
#                     dock_content.deleteLater()
#                     dock_content = None

#                 chatGPTdockWidget.close()
#                 chatGPTdockWidget.deleteLater()
#                 chatGPTdockWidget = None

#                 QCoreApplication.processEvents()

#             loop = QEventLoop()
#             QTimer.singleShot(1000, loop.quit)
#             loop.exec()
#             QCoreApplication.processEvents()


#         QTimer.singleShot(0, delayed_close)



# 🚨 add-onの更新時にAnkiがｸﾗｯｼｭするﾊﾞｸﾞがある
# gui_hooks.addon_manager_will_install_addon.remove(close_dock_widget)
# gui_hooks.addon_manager_will_install_addon.append(close_dock_widget)




        # if now_AI_type == GOOGLE_BARD:

        #     # js_code = f"""
        #     # function clickButton() {{
        #     #     var button = document.querySelector('{stop_button_class}');
        #     #     if (button) {{
        #     #         button.click();
        #     #     }}
        #     # }}
        #     # clickButton();
        #     # """

        #     js_code = f"""
        #     function clickButton() {{
        #         var button = document.querySelector('{stop_button_class}');
        #         if (button && !button.disabled && button.getAttribute('aria-disabled') !== 'true') {{
        #             button.click();
        #         }}
        #     }}
        #     clickButton();
        #     """
        #     self.webview.page().runJavaScript(js_code, self.js_callback)

        #     js_code = f"""
        #     function focusAndSelectElement(selector) {{
        #         const el = document.querySelector(selector);
        #         if (el) {{
        #             el.focus();
        #             if (el.select) {{
        #                 el.select();
        #             }}
        #             el.click();
        #         }}
        #         return el;
        #     }}
        #     setTimeout(function() {{
        #         focusAndSelectElement('{class_name}');
        #     }}, 100);
        #     """

        #     # original_clipboard_text = mw.app.clipboard().text()
        #     # # self.webview.page().runJavaScript(js_code, self.js_callback)
        #     # print("prompt_text:", prompt_text)
        #     # QTimer.singleShot(200, lambda prompt_text=prompt_text: mw.app.clipboard().setText(prompt_text))
        #     # # QTimer.singleShot(200, lambda: self.webview.triggerPageAction(QWebEnginePage.WebAction.SelectAll))
        #     # QTimer.singleShot(300, lambda: self.webview.triggerPageAction(QWebEnginePage.WebAction.Paste))
        #     # QTimer.singleShot(400, lambda original_clipboard_text=original_clipboard_text: mw.app.clipboard().setText(original_clipboard_text))

        #     original_clipboard_text = mw.app.clipboard().text()
        #     # self.webview.page().runJavaScript(js_code, self.js_callback)
        #     print("prompt_text:", prompt_text)
        #     mw.app.clipboard().setText(prompt_text)
        #     self.webview.triggerPageAction(QWebEnginePage.WebAction.Paste)
        #     # QTimer.singleShot(200, lambda: self.webview.triggerPageAction(QWebEnginePage.WebAction.Paste))

        #     js_code += f"""
        #     setTimeout(function() {{
        #         var submitButton = document.querySelector('{button_class}');
        #         if (submitButton && !submitButton.disabled && submitButton.getAttribute('aria-disabled') !== 'true') {{
        #             submitButton.click();
        #         }}
        #     }}, 200);
        #     """

        #     QTimer.singleShot(400, lambda original_clipboard_text=original_clipboard_text: mw.app.clipboard().setText(original_clipboard_text))

        #     self.webview.page().runJavaScript(js_code, self.js_callback)
        #     return