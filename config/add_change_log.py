# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

from aqt.qt import QTextBrowser, QVBoxLayout, QTabWidget, QWidget

ADDON_NAME = "Changelog"

def add_change_log_layout(layout:QVBoxLayout):
    try:
        shortcuts_tb = QTextBrowser()
        from .popup_config import NEW_FEATURE
        from .change_log import OLD_CHANGE_LOG
        change_log_text = f"[ Change log ]<br>{NEW_FEATURE}<br>{OLD_CHANGE_LOG}"
        change_log_text = change_log_text.replace("\n", "<br>")
        shortcuts_tb.setHtml(change_log_text)
        layout.addWidget(shortcuts_tb)
    except Exception as e:
        print(f"[{ADDON_NAME}] Error: {e}")


def add_change_log_tab(self, tab_widget: "QTabWidget"):
    tab_widget_widget = QWidget(self)
    layout = QVBoxLayout(tab_widget_widget)
    add_change_log_layout(layout)
    tab_widget.addTab(tab_widget_widget, "log")
