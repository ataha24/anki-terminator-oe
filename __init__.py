# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

from .config.load_pyglet import load_pyglet_and_setup
load_pyglet_and_setup()

from .add_menu import  add_g_translate
add_g_translate()

from .config.PopUpAnkiConfig import shige_config_setup
shige_config_setup()

from .config.popup_config import set_gui_hook_change_log
set_gui_hook_change_log()