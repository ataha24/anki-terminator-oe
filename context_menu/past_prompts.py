# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

# not used yet

import random
from aqt import QAction,  mw, QMenu

from typing import TYPE_CHECKING
if TYPE_CHECKING: from ..dock_web_view import ResizableWebView

def make_prompts_menu(web_view:"ResizableWebView", menu: QMenu,*args,**kwargs):
    # if not mw.state == 'review':
    #     return
    config = mw.addonManager.getConfig(__name__)
    b_name = config["button_name"]

    buttons = [
        (b_name[0], lambda: past_action(web_view, "random_prompt")),
        (b_name[1], lambda: past_action(web_view, "more_info")),
        (b_name[2], lambda: past_action(web_view, "baby_explanation")),
        (b_name[3], lambda: past_action(web_view, "word_origin")),
        (b_name[4], lambda: past_action(web_view, "make_joke")),
        (b_name[5], lambda: past_action(web_view, "history")),
        (b_name[6], lambda: past_action(web_view, "synonym")),
        (b_name[7], lambda: past_action(web_view, "mnemonic")),
    ]

    for index, (button_name, action_function) in enumerate(buttons, start=1):
        custom_action = QAction(f"{index}. {button_name}", web_view)
        custom_action.triggered.connect(action_function)
        menu.addAction(custom_action)
        print(index)

def past_action(web_view:"ResizableWebView", text, search_text=None):
    if search_text is not None: # ﾃｷｽﾄがすでに指定されている場合
        web_view.set_last_text(search_text)

        if hasattr(mw, 'reviewer') and hasattr(mw.reviewer, 'card'):
            web_view.last_card_note = mw.reviewer.card.note() # ﾚﾋﾞｭﾜｰから取得

    if web_view.last_text is not None:
        config = mw.addonManager.getConfig(__name__)
        more_info = config[text]
        more_info = random.choice(more_info)
        if "{}" in more_info:
            from ..dock_web_view import SYMBOL, CHOICE_SYMBOL
            prompt_text = more_info.format(SYMBOL[CHOICE_SYMBOL][0]
                                            + web_view.last_text
                                            + SYMBOL[CHOICE_SYMBOL][1])
        else:
            prompt_text = web_view.last_text + more_info

        prompt_text = prompt_text.replace("'", " ")
        prompt_text = prompt_text.replace('"', " ")
        prompt_text = prompt_text.replace('\n', " ")
        prompt_text = prompt_text.replace('\r', " ")

        # print(f"prompt_text: {prompt_text}")
        web_view.webpage.runJavaScript(f'document.execCommand("insertHTML", false, `{prompt_text}`);')

        # https://stackoverflow.com/questions/25941559/is-there-a-way-to-keep-execcommandinserthtml-from-removing-attributes-in-chr



        # web_view.webpage.runJavaScript(f'''
        # function insertHTML() {{
        #     var sel, range;
        #     if (window.getSelection && (sel = window.getSelection()).rangeCount) {{
        #         range = sel.getRangeAt(0);
        #         var textArea = range.startContainer.closest('textarea');
        #         var contentEditable = range.startContainer.closest('[contenteditable="true"]');

        #         if (!textArea && !contentEditable) {{
        #             var parent = range.startContainer.parentNode;
        #             while (parent && parent.nodeType === 1) {{
        #                 var textAreas = parent.getElementsByTagName('textarea');
        #                 if (textAreas.length > 0) {{
        #                     textArea = textAreas[0];
        #                     break;
        #                 }}
        #                 if (parent.hasAttribute('contenteditable') && parent.getAttribute('contenteditable') === 'true') {{
        #                     contentEditable = parent;
        #                     break;

        #                 parent = parent.parentNode;
        #             }}
        #         }}


        #         if (textArea) {{
        #             var startPos = textArea.selectionStart;
        #             var endPos = textArea.selectionEnd;
        #             var text = textArea.value;
        #             var before = text.substring(0, startPos);
        #             var after = text.substring(endPos, text.length);
        #             textArea.value = before + "{prompt_text}" + after;
        #             textArea.selectionStart = textArea.selectionEnd = startPos + "{prompt_text}".length;

        #         }} else if (contentEditable) {{
        #             range.collapse(true);
        #             var textNode = document.createTextNode("{prompt_text}");
        #             range.insertNode(textNode);

        #             // Move the caret immediately after the inserted text node
        #             range.setStartAfter(textNode);
        #             range.collapse(true);
        #             sel.removeAllRanges();
        #             sel.addRange(range);

        #     }}
        # }}}}
        # insertHTML();
        # ''')


        # web_view.webpage.runJavaScript(f'''
        # function insertHTML() {{
        #     var sel, range;
        #     if (window.getSelection && (sel = window.getSelection()).rangeCount) {{
        #         range = sel.getRangeAt(0);
        #         var textArea = range.startContainer.closest('textarea');

        #         if (!textArea) {{
        #             var parent = range.startContainer.parentNode;
        #             while (parent && parent.nodeType === 1) {{
        #                 var textAreas = parent.getElementsByTagName('textarea');
        #                 if (textAreas.length > 0) {{
        #                     textArea = textAreas[0];
        #                     break;
        #                 }}
        #                 parent = parent.parentNode;
        #             }}
        #         }}


        #         if (textArea) {{
        #             var startPos = textArea.selectionStart;
        #             var endPos = textArea.selectionEnd;
        #             var text = textArea.value;
        #             var before = text.substring(0, startPos);
        #             var after = text.substring(endPos, text.length);
        #             textArea.value = before + "{prompt_text}" + after;
        #             textArea.selectionStart = textArea.selectionEnd = startPos + "{prompt_text}".length;

        #     }}
        # }}}}
        # insertHTML();
        # ''')

                # }} else {{
                #     range.collapse(true);
                #     var textNode = document.createTextNode("{prompt_text}");
                #     range.insertNode(textNode);

                #     // Move the caret immediately after the inserted text node
                #     range.setStartAfter(textNode);
                #     range.collapse(true);
                #     sel.removeAllRanges();
                #     sel.addRange(range);
                # }}


        # web_view.webpage.runJavaScript(f'''
        # function insertHTML() {{
        #     var sel, range;
        #     if (window.getSelection && (sel = window.getSelection()).rangeCount) {{
        #         range = sel.getRangeAt(0);
        #         range.collapse(true);
        #         var textNode = document.createTextNode("{prompt_text}");
        #         range.insertNode(textNode);

        #         // Move the caret immediately after the inserted text node
        #         range.setStartAfter(textNode);
        #         range.collapse(true);
        #         sel.removeAllRanges();
        #         sel.addRange(range);
        #     }}
        # }}
        # insertHTML();
        # ''')


        # web_view.webpage.runJavaScript(f'''
        #     function insertHTML() {{
        #         var sel, range;
        #         if (window.getSelection && (sel = window.getSelection()).rangeCount) {{
        #             range = sel.getRangeAt(0);
        #             range.collapse(true);
        #             var span = document.createElement("span");
        #             span.id = "myId";
        #             span.appendChild(document.createTextNode("{prompt_text}"));
        #             range.insertNode(span);

        #             // Move the caret immediately after the inserted span
        #             range.setStartAfter(span);
        #             range.collapse(true);
        #             sel.removeAllRanges();
        #             sel.addRange(range);
        #         }}
        #     }}
        #     insertHTML();
        # ''')