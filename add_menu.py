# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

from aqt import QAction, QIcon, QKeySequence, mw
from os.path import join, dirname
# from .my_web_view import Web_view
from aqt import gui_hooks
from .update_top_toolbar import setup_update_top_toolbar, ChatGPT_URL_open
from .path_manager import ADDON_TITLE

print(
r"""
     _    _   _ _  _____   _____ _____ ____  __  __ ___ _   _    _  _____ ___  ____
    / \  | \ | | |/ /_ _| |_   _| ____|  _ \|  \/  |_ _| \ | |  / \|_   _/ _ \|  _ \
   / _ \ |  \| | ' / | |    | | |  _| | |_) | |\/| || ||  \| | / _ \ | || | | | |_) |
  / ___ \| |\  | . \ | |    | | | |___|  _ <| |  | || || |\  |/ ___ \| || |_| |  _ <
 /_/   \_\_| \_|_|\_\___|   |_| |_____|_| \_\_|  |_|___|_| \_/_/   \_\_| \___/|_| \_\

by Shige
"""
)
# Font Name: Standard

menu_action = None

def add_menu_bar(icon, name, func):
    global menu_action
    menu = QAction(icon,name, mw)
    menu.triggered.connect(func)

    from .make_manu import get_anki_terminator_menu
    get_anki_terminator_menu().addAction(menu)
    # mw.form.menuTools.addAction(menu)

    config = mw.addonManager.getConfig(__name__)
    menu_shortcut = config["AI_shortcut_key"]
    menu.setShortcut(QKeySequence(menu_shortcut))
    menu_action = menu

def add_g_translate():
    addon_path = dirname(__file__)
    icon_path = join(addon_path, r'ChatGPT_logo.png')
    ChatGPT_logo_icon = QIcon(icon_path)
    add_menu_bar(ChatGPT_logo_icon, ADDON_TITLE, ChatGPT_URL_open)

def setup_chatGPTwidget():
    config = mw.addonManager.getConfig(__name__)
    if config["start_up"]:
        ChatGPT_URL_open()

gui_hooks.main_window_did_init.append(setup_chatGPTwidget)

# setup_chatGPTwidget_executed = False
# def setup_chatGPTwidget(new_state, old_state, *args, **kwargs):
#     global setup_chatGPTwidget_executed
#     # mw.state == "deckBrowser"
#     if new_state == "review":
#         config = mw.addonManager.getConfig(__name__)
#         if config["start_up"]:
#             ChatGPT_URL_open()
#     setup_chatGPTwidget_executed = True

# gui_hooks.main_window_did_init.remove(setup_chatGPTwidget)
# gui_hooks.main_window_did_init.append(setup_chatGPTwidget)

# gui_hooks.state_did_change.append(setup_chatGPTwidget)

setup_update_top_toolbar()