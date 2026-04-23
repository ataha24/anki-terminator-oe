# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

from aqt import QPushButton, QSizePolicy, Qt

def mini_button(button:QPushButton):
    button.setStyleSheet("QPushButton { padding: 2px; }")
    button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    button.setFocusPolicy(Qt.FocusPolicy.NoFocus)