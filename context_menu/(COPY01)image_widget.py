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

        # js_code = f"""
        # var elementToHover = document.querySelector('{stop_button_class}');
        # if (elementToHover) {{
        #     var event = new MouseEvent('mouseover', {{
        #         view: window,
        #         bubbles: true,
        #         cancelable: true
        #     }});
        #     elementToHover.dispatchEvent(event);
        # }}

        # setTimeout(function() {{
        # var buttons = document.querySelectorAll('{stop_button_class}');
        # buttons.forEach(function(button) {{
        #     var icon = button.querySelector('i.material-icons');
        #     if (icon && icon.textContent.trim() === 'restart_alt') {{
        #         button.click();
        #     }}
        # }});
        # }}, 300);
        # """

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

         
        # js_code = f"""
        # function focusAndSelectElement(selector, text) {{
        #     const el = document.querySelector(selector);
        #     if (el) {{
        #         el.focus();
        #         if (el.select) {{
        #             el.select();
        #         }}
        #         el.click();

        #         setTimeout(() => {{
        #             // Ctrl + A
        #             el.dispatchEvent(new KeyboardEvent('keydown', {{key: 'Control', ctrlKey: true, bubbles: true}}));
        #             el.dispatchEvent(new KeyboardEvent('keydown', {{key: 'a', ctrlKey: true, bubbles: true}}));
        #             el.dispatchEvent(new KeyboardEvent('keyup', {{key: 'Control', ctrlKey: true, bubbles: true}}));
        #             el.dispatchEvent(new KeyboardEvent('keyup', {{key: 'a', ctrlKey: true, bubbles: true}}));

        #             // Backspace
        #             el.dispatchEvent(new KeyboardEvent('keydown', {{key: 'Backspace', bubbles: true}}));
        #             el.dispatchEvent(new KeyboardEvent('keyup', {{key: 'Backspace', bubbles: true}}));
        #         }}, 300);

        #         setTimeout(() => {{
        #             for (let char of text) {{
        #                 el.dispatchEvent(new KeyboardEvent('keydown', {{key: char, bubbles: true}}));
        #                 el.dispatchEvent(new KeyboardEvent('keyup', {{key: char, bubbles: true}}));
        #             }}
        #         }}, 500);
        #     }}
        #     return el;
        # }}
        # focusAndSelectElement('{class_name}', '{text}');
        # """

        # js_code += f"""
        # setTimeout(function() {{
        #     var submitButton = document.querySelector('{button_class}');
        #     if (submitButton && !submitButton.disabled && submitButton.getAttribute('aria-disabled') !== 'true') {{
        #         submitButton.click();
        #     }}
        # }}, 700);
        # """
         

        # js_code = f"""
        # function focusAndSelectElement(selector, text, newText) {{
        #     const el = document.querySelector(selector);
        #     if (el) {{
        #         el.focus();
        #         if (el.select) {{
        #             el.select();
        #         }}
        #         el.click();
        #         setTimeout(() => {{
        #             for (let char of text) {{
        #                 el.dispatchEvent(new KeyboardEvent('keydown', {{key: char, bubbles: true}}));
        #                 el.dispatchEvent(new KeyboardEvent('keypress', {{key: char, bubbles: true}}));
        #                 el.dispatchEvent(new KeyboardEvent('keyup', {{key: char, bubbles: true}}));
        #             }}
        #         }}, 300);


        #         setTimeout(() => {{
        #             function findAndReplaceInSlateString(node, text, newText) {{
        #                 if (node.hasAttribute && node.getAttribute('data-slate-string') === 'true') {{
        #                     const startIndex = node.textContent.indexOf(text);
        #                     if (startIndex !== -1) {{
        #                         const range = document.createRange();
        #                         range.setStart(node.firstChild, startIndex);
        #                         range.setEnd(node.firstChild, startIndex + text.length);
        #                         const selection = window.getSelection();
        #                         selection.removeAllRanges();
        #                         selection.addRange(range);
        #                         document.execCommand('insertText', false, newText);
        #                         return true;
        #                     }}
        #                 }}
        #                 for (let child of node.childNodes) {{
        #                     if (findAndReplaceInSlateString(child, text, newText)) {{
        #                         return true;
        #                     }}
        #                 }}
        #                 return false;
        #             }}
        #             findAndReplaceInSlateString(el, text, newText);
        #         }}, 600);

        #     }}
        #     return el;
        # }}
        # focusAndSelectElement('{class_name}', 'shigetest', '{text}');
        # """


        # js_code = f"""
        # function focusAndSelectElement(selector) {{
        #     const el = document.querySelector(selector);
        #     if (el) {{
        #         el.focus();
        #         if (el.select) {{
        #             el.select();
        #         }}
        #         el.click();

        #         el.dispatchEvent(new KeyboardEvent('keydown', {{key: 't', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keypress', {{key: 't', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keyup', {{key: 't', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keydown', {{key: 'e', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keypress', {{key: 'e', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keyup', {{key: 'e', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keydown', {{key: 's', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keypress', {{key: 's', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keyup', {{key: 's', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keydown', {{key: 't', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keypress', {{key: 't', bubbles: true}}));
        #         el.dispatchEvent(new KeyboardEvent('keyup', {{key: 't', bubbles: true}}));

        #     }}
        #     return el;
        # }}
        # focusAndSelectElement('{class_name}');
        # """

        # js_code = f"""
        # function replaceValue(selector, value) {{
        # const el = document.querySelector(selector);
        # if (el) {{
        #     el.focus();
        #     document.execCommand('selectAll');
        #     if (!document.execCommand('insertText', false, value)) {{
        #     el.value = '{text}';
        #     }}
        #     el.dispatchEvent(new Event('change', {{bubbles: true}}));
        # }}
        # return el;
        # }}
        # replaceValue('{class_name}', '{text}');
        # """

        # self.web_view.page().runJavaScript(js_code, self.js_callback)
        # QTimer.singleShot(100, lambda: self.web_view.triggerPageAction(QWebEnginePage.WebAction.SelectAll))
        # QTimer.singleShot(200, lambda: self.web_view.triggerPageAction(QWebEnginePage.WebAction.Paste))

        # origin_clip_text = mw.app.clipboard().text()

        self.clipboard = mw.app.clipboard()
        original_data = self.clipboard.mimeData(QClipboard.Mode.Clipboard)
        self.original_clipboard_data = QMimeData()
        for format in original_data.formats():
            # print(" - format:", format)
            self.original_clipboard_data.setData(format, original_data.data(format))

        QTimer.singleShot(100, lambda prompts_text=prompts_text : mw.app.clipboard().setText(prompts_text))
        QTimer.singleShot(200, lambda: self.web_view.triggerPageAction(QWebEnginePage.WebAction.SelectAll))
        QTimer.singleShot(300, lambda: self.web_view.triggerPageAction(QWebEnginePage.WebAction.Paste))

        js_code += f"""
        setTimeout(function() {{
            var submitButton = document.querySelector('{button_class}');
            if (submitButton && !submitButton.disabled && submitButton.getAttribute('aria-disabled') !== 'true') {{
                submitButton.click();
            }}
        }}, 400);
        """

        QTimer.singleShot(500, lambda origin_clip_text=origin_clip_text : mw.app.clipboard().setText(origin_clip_text))

        self.web_view.page().runJavaScript(js_code, self.js_callback)

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