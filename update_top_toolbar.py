# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

import os

from aqt import mw, gui_hooks
from aqt.utils import tooltip
from aqt.toolbar import Toolbar

from .dock_web_view import Web_view
from .path_manager import (CHAT_GPT, GOOGLE_BARD, BING_CHAT,CUSTOM_AI,
                            CHAT_GPT_LOGO, GOOGLE_BARD_LOGO, BING_CHAT_LOGO,CUSTOM_LOGO,
                            LABEL_TEXT,LABEL_ID,LABEL_PYCMD,LABEL_INDEX,
                            DEEP_SEEK, DEEP_SEEK_URL,DEEP_SEEK_LOGO,
                            PERPLEXITY, PERPLEXITY_URL, PERPLEXITY_LOGO,
                            CLAUDE, CLAUDE_URL,CLAUDE_LOGO,
                            IMAGE_FX, IMAGE_FX_URL, IMAGE_FX_LOGO,
                            GROK_AI, GROK_AI_URL, GROK_LOGO,
                            DUCK_AI, DUCK_AI_URL, DUCK_AI_LOGO,
                            OPEN_EVIDENCE, OPEN_EVIDENCE_URL,
                            )


def ChatGPT_URL_open():
    config = mw.addonManager.getConfig(__name__)
    now_AI_type = config["now_AI_type"]

    if (DEEP_SEEK not in config["ChatGPT_URL"]
        or PERPLEXITY not in config["ChatGPT_URL"]
        or CLAUDE not in config["ChatGPT_URL"]
        or IMAGE_FX not in config["ChatGPT_URL"]
        ):
        config["ChatGPT_URL"][DEEP_SEEK] = DEEP_SEEK_URL
        config["ChatGPT_URL"][PERPLEXITY] = PERPLEXITY_URL
        config["ChatGPT_URL"][CLAUDE] = CLAUDE_URL
        config["ChatGPT_URL"][IMAGE_FX] = IMAGE_FX_URL
        mw.addonManager.writeConfig(__name__, config)

    if (GROK_AI not in config["ChatGPT_URL"]
        ):
        config["ChatGPT_URL"][GROK_AI] = GROK_AI_URL
        mw.addonManager.writeConfig(__name__, config)

    if (DUCK_AI not in config["ChatGPT_URL"]
        ):
        config["ChatGPT_URL"][DUCK_AI] = DUCK_AI_URL
        mw.addonManager.writeConfig(__name__, config)

    if OPEN_EVIDENCE not in config["ChatGPT_URL"]:
        config["ChatGPT_URL"][OPEN_EVIDENCE] = OPEN_EVIDENCE_URL
        mw.addonManager.writeConfig(__name__, config)

    if now_AI_type in config["ChatGPT_URL"]:
        ChatGPT_URL = config["ChatGPT_URL"][now_AI_type]
    elif not config["Custom_AI_URL"].isspace():
        ChatGPT_URL = config["Custom_AI_URL"]
    else: # ﾃﾞﾌｫﾙﾄ
        ChatGPT_URL = CHAT_GPT

    Web_view("ChatGPT",ChatGPT_URL)


def add_gpt_to_the_top_toolbar(links: list, toolbar: Toolbar) -> None:
    try:
        config = mw.addonManager.getConfig(__name__)
        now_AI_type = config["now_AI_type"]
        if now_AI_type == CHAT_GPT:
            logo_png = CHAT_GPT_LOGO
        elif now_AI_type == GOOGLE_BARD:
            logo_png = GOOGLE_BARD_LOGO
        elif now_AI_type == BING_CHAT:
            logo_png = BING_CHAT_LOGO
        elif now_AI_type == DEEP_SEEK:
            logo_png = DEEP_SEEK_LOGO
        elif now_AI_type == PERPLEXITY:
            logo_png = PERPLEXITY_LOGO
        elif now_AI_type == CLAUDE:
            logo_png = CLAUDE_LOGO
        elif now_AI_type == IMAGE_FX:
            logo_png = IMAGE_FX_LOGO
        elif now_AI_type == GROK_AI:
            logo_png = GROK_LOGO
        elif now_AI_type == DUCK_AI:
            logo_png = DUCK_AI_LOGO

        elif now_AI_type == OPEN_EVIDENCE:
            logo_png = None  # text-only label

        # elif now_AI_type == CUSTOM_AI:
        #     logo_png = CUSTOM_LOGO

        else:
            logo_png = LABEL_TEXT

        if logo_png is None:
            html_label = "OE"
        elif logo_png == LABEL_TEXT:
            html_label = LABEL_TEXT
        else:
            mw.addonManager.setWebExports(__name__, r".*")
            addon_package = mw.addonManager.addonFromModule(__name__)
            mediafolder = f"/_addons/{addon_package}/{logo_png}"
            # ﾀﾞﾌﾞﾙｸｫﾃｰｼｮﾝにするとﾊﾞｸﾞる､ｼﾝｸﾞﾙならｷﾞﾘいける
            html_label = f"<img src='{mediafolder}' alt='{LABEL_TEXT}' style='height: 1em;'>"

        shortcut_key = config["AI_shortcut_key"]

        def create_link(cmd,label,func,tip,id,):#aria-labelがHTMLになるとﾊﾞｸﾞる
            toolbar.link_handlers[cmd] = func
            title_attr = f'title="{tip}"' if tip else ""
            id_attr = f'id="{id}"' if id else ""
            return (
                f"""<a class=hitem tabindex="-1" aria-label="{LABEL_TEXT}" """
                f"""{title_attr} {id_attr} href=# onclick="return pycmd('{cmd}')">"""
                f"""{label}</a>"""
            )

        link = create_link(
            cmd = LABEL_PYCMD,
            label = html_label,
            func = ChatGPT_URL_open,
            tip = f"Open Sidebar ( {shortcut_key} )" ,
            id = LABEL_ID ,
        )
        links.insert(LABEL_INDEX, link)
    except:
        pass


def setup_update_top_toolbar():
    if mw is not None:
        config = mw.addonManager.getConfig(__name__)
        if config["add_gpt_to_the_top_toolbar"]:
            gui_hooks.top_toolbar_did_init_links.remove(add_gpt_to_the_top_toolbar)
            gui_hooks.top_toolbar_did_init_links.append(add_gpt_to_the_top_toolbar)

# Inspired by this add-on👍👍👍
# AJT Flexible Grading / Tatsumoto
# https://ankiweb.net/shared/info/1715096333
# https://github.com/Ajatt-Tools/FlexibleGrading


def change_AI_icon_on_top_tool_bar():
    config = mw.addonManager.getConfig(__name__)
    now_AI_type = config["now_AI_type"]
    if now_AI_type == CHAT_GPT:
        logo_png = CHAT_GPT_LOGO
    elif now_AI_type == GOOGLE_BARD:
        logo_png = GOOGLE_BARD_LOGO
    elif now_AI_type == BING_CHAT:
        logo_png = BING_CHAT_LOGO
    elif now_AI_type == DEEP_SEEK:
        logo_png = DEEP_SEEK_LOGO
    elif now_AI_type == PERPLEXITY:
        logo_png = PERPLEXITY_LOGO
    elif now_AI_type == CLAUDE:
        logo_png = CLAUDE_LOGO
    elif now_AI_type == IMAGE_FX:
        logo_png = IMAGE_FX_LOGO
    elif now_AI_type == GROK_AI:
        logo_png = GROK_LOGO
    elif now_AI_type == DUCK_AI:
        logo_png = DUCK_AI_LOGO

    elif now_AI_type == OPEN_EVIDENCE:
        logo_png = None  # text-only label

    # elif now_AI_type == CUSTOM_AI:
    #     logo_png = CUSTOM_LOGO

    else:
        logo_png = LABEL_TEXT

    if logo_png is None:
        new_label = "OE"
    elif logo_png == LABEL_TEXT:
        new_label = LABEL_TEXT
    else:
        mw.addonManager.setWebExports(__name__, r".*")
        addon_package = mw.addonManager.addonFromModule(__name__)
        mediafolder = f"/_addons/{addon_package}/{logo_png}"
        # ﾀﾞﾌﾞﾙｸｫﾃｰｼｮﾝにするとﾊﾞｸﾞる､ｼﾝｸﾞﾙならｷﾞﾘいける
        new_label = f"<img src='{mediafolder}' alt='{LABEL_TEXT}' style='height: 1em;'>"

    js_code = f"""
    {{
        const elem = document.getElementById("{LABEL_ID}");
        elem.innerHTML = "{new_label}";
    }};
    """
    mw.toolbar.web.eval(js_code)
    show_tooltip_ai(logo_png, now_AI_type)


def show_tooltip_ai(logo_png, now_AI_type):
    try:
        display_name = now_AI_type.replace("_", " ")
        if logo_png is None:
            tooltip(f"<span style='font-size:19px;'> {display_name} </span>")
        else:
            addon_path = os.path.dirname(__file__)
            tooltip(
                f"<img src='{os.path.join(addon_path, logo_png)}' height='24'>"
                f"<span style='font-size:19px;'> {display_name} </span>")
    except Exception as e:
        print(f"[AnkiTerminatorV2] Error: {e}")



# <a class="hitem" tabindex="-1"
# aria-label="AI" title="Ctrl+G"
# id="shige_chatGPT" href="#"
# onclick="return pycmd('shige_chatGPT_toolbar_clicked')">
# AI</a>


# def add_gpt_to_the_top_toolbar(links: list, toolbar: Toolbar) -> None:
#     try:
#         config = mw.addonManager.getConfig(__name__)
#         # now_AI_type = config["now_AI_type"]
#         # if now_AI_type == CHAT_GPT:
#         #     logo_png = CHAT_GPT_LOGO
#         # elif now_AI_type == GOOGLE_BARD:
#         #     logo_png = GOOGLE_BARD_LOGO
#         # elif now_AI_type == BING_CHAT:
#         #     logo_png = BING_CHAT_LOGO
#         # else:
#         #     logo_png = LABEL_TEXT

#         # if logo_png == LABEL_TEXT:
#         #     label = LABEL_TEXT
#         # else:
#         #     mw.addonManager.setWebExports(__name__, r".*")
#         #     addon_package = mw.addonManager.addonFromModule(__name__)
#         #     mediafolder = f"/_addons/{addon_package}/{logo_png}"
#         #     # ﾀﾞﾌﾞﾙｸｫﾃｰｼｮﾝにするとﾊﾞｸﾞる､ｼﾝｸﾞﾙならｷﾞﾘいける
#         #     label = f"<img src='{mediafolder}' alt='AI' style='height: 1em;'>"

#         label = LABEL_TEXT

#         shortcut_key = config["AI_shortcut_key"]

#         link = toolbar.create_link(
#             LABEL_PYCMD,
#             label,
#             ChatGPT_URL_open,
#             tip= shortcut_key ,
#             id= LABEL_ID ,
#         )
#         links.insert(LABEL_INDEX, link)
#     except:
#         pass