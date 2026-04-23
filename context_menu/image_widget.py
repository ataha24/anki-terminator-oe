# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

import re
from aqt import QClipboard, QHBoxLayout, QMimeData, QWebEnginePage, mw
from aqt.qt import QWidget, QVBoxLayout, QTimer, QUrl, QCheckBox, Qt
from typing import TYPE_CHECKING

from ..path_manager import IMAGE_FX
if TYPE_CHECKING: from ..dock_web_view import CustomWebEnginePage

class CustomImageWidget(QWidget):
    def __init__(self, original_page: "CustomWebEnginePage", parent=None):
        super().__init__(parent)

        self.setWindowTitle("🤖AnkiTerminator Created by Shigeඞ")
        self.resize(500, 600)

        from ..dock_web_view import CustomWebEngineView, CustomWebEnginePage
        from ..path_manager import IMAGE_FX_URL

        self.web_view = CustomWebEngineView(self)
        self.new_page = CustomWebEnginePage(original_page.profile(), self.web_view)
        self.web_view.setPage(self.new_page)

        self.web_view.setUrl(QUrl(IMAGE_FX_URL))

        self.main_layout = QVBoxLayout(self)

        buttons_layout = QHBoxLayout(self)
        self.checkbox = QCheckBox("Always on top", self)
        self.checkbox.stateChanged.connect(self.toggle_on_top)
        buttons_layout.addWidget(self.checkbox)
        buttons_layout.addStretch()

        self.main_layout.addLayout(buttons_layout)

        self.main_layout.addWidget(self.web_view)

        self.setLayout(self.main_layout)

    def toggle_on_top(self, state):
        if state == 2:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.show()
        self.raise_()


    ### clip bord ###
    def restore_clipboard(self):
        if isinstance(self.original_clipboard_data, QMimeData):
            self.clipboard.clear()
            self.clipboard.setMimeData(self.original_clipboard_data, QClipboard.Mode.Clipboard)
            self.original_clipboard_data = None

    def paste_from_clipboard_02(self):
        self.web_view.triggerPageAction(QWebEnginePage.WebAction.Paste)
        self.auto_send_prompt_text = None
        print("> paste done")

    def paste_from_clipboard(self):
        print("> run paste_from_clipboard")
        if self.auto_send_prompt_text:
            if self.auto_send_prompt_text == self.clipboard.text():
                self.web_view.triggerPageAction(QWebEnginePage.WebAction.SelectAll)
                QTimer.singleShot(100, self.paste_from_clipboard_02)
            else:
                print("!None prompt")

    def send_prompts(self, prompts_text:str):

        prompts_text = re.sub(r'<[^>]*>', '', prompts_text)
        # text = text.replace("'", "\\'")
        # text = text.replace('"', '\\"')
        # text = text.replace('\n', '\\n')
        # text = text.replace('\r', '\\n')
        # text = re.sub(r'[^a-zA-Z ,:.;-]', '', text)

        config = mw.addonManager.getConfig(__name__)
        now_AI_type = config.get("sub_AI_type", IMAGE_FX)
        self.show()
        self.raise_()
        self.activateWindow()

        if now_AI_type == IMAGE_FX:
            class_name = '[role="textbox"]'#'[data-slate-node="element"]'#[role="textbox"]'
            button_class = '.sc-6eb6c34b-1' #'sc-ea6b42d1-0'

            stop_button_class = '.sc-6d40a594-0.gWJQKj.sc-97dfbf0f-1'
        else:
            return

        js_code = f"""
        function focusAndSelectElement(selector) {{
            const el = document.querySelector(selector);
            if (el) {{
                el.focus();
                if (el.select) {{
                    el.select();
                }}
                el.click();

            }}
            return el;
        }}
        focusAndSelectElement('{class_name}');
        """

        self.clipboard = mw.app.clipboard()
        original_data = self.clipboard.mimeData(QClipboard.Mode.Clipboard)
        self.original_clipboard_data = QMimeData()
        for format in original_data.formats():
            self.original_clipboard_data.setData(format, original_data.data(format))

        print("prompt_text:", prompts_text)
        self.clipboard.clear()
        self.clipboard.setText(prompts_text)
        self.auto_send_prompt_text = prompts_text
        QTimer.singleShot(500, self.paste_from_clipboard)

        js_code += f"""
        setTimeout(function() {{
            var submitButton = document.querySelector('{button_class}');
            if (submitButton && !submitButton.disabled && submitButton.getAttribute('aria-disabled') !== 'true') {{
                submitButton.click();
            }}
        }}, 700);
        """

        self.web_view.page().runJavaScript(js_code, self.js_callback)

        QTimer.singleShot(800, self.restore_clipboard)

    def js_callback(self, result):
        print("JavaScript result: ", result)


def send_prompts(text):
    if hasattr(mw, "AnkiTerminator_image_Ai_dialog"):
        if isinstance(mw.AnkiTerminator_image_Ai_dialog, CustomImageWidget):
            mw.AnkiTerminator_image_Ai_dialog.send_prompts(text)
            mw.AnkiTerminator_image_Ai_dialog.show()
            mw.AnkiTerminator_image_Ai_dialog.raise_()




def make_image_ai_widget(original_page: "CustomWebEnginePage"):
    if hasattr(mw, "AnkiTerminator_image_Ai_dialog"):
        if isinstance(mw.AnkiTerminator_image_Ai_dialog, CustomImageWidget):
            mw.AnkiTerminator_image_Ai_dialog.show()
            mw.AnkiTerminator_image_Ai_dialog.raise_()
            return

    # from ..dock_web_view import close_all_dock_widget
    mw.AnkiTerminator_image_Ai_dialog = new_dialog = CustomImageWidget(original_page)

    QTimer.singleShot(0, new_dialog.show)
    QTimer.singleShot(0, new_dialog.raise_)



# from aqt import mw
# from aqt.qt import QWidget, QVBoxLayout, QTimer, QUrl
# from typing import TYPE_CHECKING
# if TYPE_CHECKING: from ..dock_web_view import CustomWebEngineView, CustomWebEnginePage

# def make_image_ai_widget(original_page:"CustomWebEnginePage"):
#     if hasattr(mw, "AnkiTerminator_image_Ai_dialog"):
#         if isinstance(mw.AnkiTerminator_image_Ai_dialog, QWidget):
#             mw.AnkiTerminator_image_Ai_dialog.show()
#             mw.AnkiTerminator_image_Ai_dialog.raise_()
#             return

#     from ..dock_web_view import CustomWebEngineView, CustomWebEnginePage
#     from ..path_manager import IMAGE_FX_URL

#     # from ..dock_web_view import close_all_dock_widget
#     mw.AnkiTerminator_image_Ai_dialog = new_dialog = QWidget(None)

#     new_dialog.setWindowTitle("🤖AnkiTerminator Created by Shigeඞ")
#     new_dialog.resize(500, 600)
#     web_view = CustomWebEngineView(new_dialog)
#     new_page = CustomWebEnginePage(original_page.profile(), web_view)
#     web_view.setPage(new_page)
#     web_view.setUrl(QUrl(IMAGE_FX_URL))
#     layout = QVBoxLayout(new_dialog)
#     layout.addWidget(web_view)
#     new_dialog.setLayout(layout)

#     QTimer.singleShot(0, new_dialog.show)