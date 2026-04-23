# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

import os
import random
from aqt import QAction, QApplication, QDialog, QFrame, QGroupBox, QHBoxLayout, QKeySequence, QLineEdit, QRadioButton, QSizePolicy
from aqt import QRectF, QSlider, QTabWidget, QTimer, QWidget,Qt
from aqt import QVBoxLayout, QLabel, QPushButton,gui_hooks, QMenu, QPainter, qconnect
from aqt import QDoubleSpinBox, mw
from aqt.utils import showInfo,tr
from os.path import join, dirname
from aqt import QIcon, QPainterPath
from aqt import QPixmap
from aqt.utils import openLink,tooltip
from aqt import QMessageBox,QCheckBox

from . import listOfSupportedPatrons as CreditData
from .endroll.endroll import add_credit_tab
from ..path_manager import ADDON_TITLE_2,THEMES,CUSTOM_AI
from ..shigetr import shige_tr,qtip_style
from .shige_addons import add_shige_addons_tab
from .add_change_log import add_change_log_tab

from ..shige_tools.open_shige_addons_wiki import WikiQLabel


#📍
WIDGET_WIDTH = 629
WIDGET_HEIGHT = 586
# Width: 629, Height: 586


SET_WINDOW_TITLE = ADDON_TITLE_2
ADDON_BANNER_IMAGE = r"banner.jpg"
PATREON_BANNER_JPG = r"Patreon_banner.jpg"
DIALOG_ICON = r"icon.png"

PATREON_LINK_URL = "http://patreon.com/Shigeyuki"
SET_SCALEDTOWIDTH = 500
SET_LINE_EDID_WIDTH = 400
MAX_LABEL_WIDTH = 80
MAX_HEIGHT = 500

ICON_PATH = r"media/sprite/progKnight/config/icon.png"
BANNER_PATH =r"media/sprite/progKnight/config/banner.jpg"

CURLY_BRACES = r" {} "

TAB_ONE = "Prompt"
TAB_TWO = "Always"
TAB_THREE = "Exclude"
TAB_FOUR = "Other"
TAB_FIVE = "Tags"
TAB_SIX = "Credit"
TAB_SEVEN = "Fields"

SOUND_OPEN = r"open"
SOUND_SELECT = r"select"
SOUND_OPENLINK = r"openlink"
SOUND_OK = r"OK"
SOUND_CANCEL = r"cancel"
SOUND_SYSTEM = r"system_sounds"
CONFIG_FOLDER = r"config"
THEME_CHANGE = r"themeChange"

this_addon_menu = None

IS_CHANGE_LOG = None
ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
# ｱﾄﾞｵﾝのURLが数値であるか確認
if (isinstance(ADDON_PACKAGE, (int, float))
    or (isinstance(ADDON_PACKAGE, str)
    and ADDON_PACKAGE.isdigit())):
    RATE_THIS = True

IS_CHANGE_LOG = True
RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"



# ---- ﾌｫﾝﾄの設定画面を作成するｸﾗｽ --------
class SetPopupConfig(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)


        self.TAB_ONE = shige_tr.Prompts
        self.TAB_TWO = shige_tr.Always
        self.TAB_THREE = shige_tr.Exclude
        self.TAB_FOUR = shige_tr.Other
        self.TAB_FIVE = shige_tr.Tags
        self.TAB_SIX = shige_tr.Credit
        self.TAB_SEVEN = shige_tr.Fields


        # 作成手順のﾒﾓ
        # configを変数に登録
        # 変数をQCheckBoxに登録
        # Qﾗﾍﾞﾙに追加
        # ﾎﾞﾀﾝを押したときの動作を設定
        # configを上書き
        #--------------------

        config = mw.addonManager.getConfig(__name__)

        # button_name_list
        self.b_name = config["button_name"]


        # list 1
        self.random_prompt = config["random_prompt"]
        self.exclusion_list = config["exclusion_list"]
        self.more_info = config["more_info"]

        self.baby_explanation = config["baby_explanation"]

        self.word_origin = config["word_origin"]
        self.make_joke = config["make_joke"]
        self.history = config["history"]
        self.synonym = config["synonym"]
        self.mnemonic = config["mnemonic"]

        # list 2
        self.i_am_studying = config["i_am_studying"]
        self.language = config["language"]

        # list 3
        self.Priority_tag_list = config["Priority_tag_list"]
        self.Priority_Fields_list = config["Priority_Fields_list"]

        # toggle 1
        self.is_i_am_studying = config["is_i_am_studying"]
        self.change_Language = config["change_Language"]

        # toggle 2
        self.start_up = config["start_up"]
        self.add_gpt_to_the_top_toolbar = config["add_gpt_to_the_top_toolbar"]
        # self.input_text = config["input_text"]
        self.submit_text = config["submit_text"]
        self.hide_the_sidebar_on_the_answer_screen = config["hide_the_sidebar_on_the_answer_screen"]

        # AI type
        self.now_AI_type = config["now_AI_type"]


        # shortcut keys
        self.Enter_Short_cut_Key = config["Enter_Short_cut_Key"]
        self.AI_shortcut_key = config["AI_shortcut_key"]

        # last_tab
        self.last_tab = config["last_tab"]

        # custom Ai
        self.Custom_Ai = config["Custom_Ai"]
        self.Custom_AI_URL = config["Custom_AI_URL"]

        self.effect_volume = config.get("EffectVolume", 0.5)
        self.auto_read_aloud = config.get("auto_read_aloud", True)

        # paste images
        self.image_width = config.get("image_width", 300)

        # no auto press
        self.no_auto_press_send_button = config.get("no_auto_press_send_button", False)

        #--------------------
        # Set window icon
        addon_path = dirname(__file__)
        self.icon_path = join(addon_path, DIALOG_ICON)
        self.logo_icon = QIcon(self.icon_path)
        self.setWindowIcon(self.logo_icon)


        # 背景画像を設定----------------------------------
        # ｱﾌﾟﾘｹｰｼｮﾝ全体のｽﾀｲﾙｼｰﾄを取得して適用します
        app_style = QApplication.instance().styleSheet()
        self.check_Anki_Style_existence = False
        if app_style:
            self.check_Anki_Style_existence = True


        # Patreonﾗﾍﾞﾙ-----------------------------------
        self.patreon_label = QLabel()
        self.addon_banner_image = join(addon_path, ADDON_BANNER_IMAGE)

        patreon_banner_path = join(addon_path, self.addon_banner_image)
        pixmap = QPixmap(patreon_banner_path)
        pixmap = pixmap.scaledToWidth(SET_SCALEDTOWIDTH, Qt.TransformationMode.SmoothTransformation)

        path = QPainterPath()
        path.addRoundedRect(QRectF(pixmap.rect()), 10, 10)  # 角の丸み
        rounded_pixmap = QPixmap(pixmap.size())
        rounded_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        pixmap = rounded_pixmap

        self.patreon_label.setPixmap(pixmap)
        self.patreon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.patreon_label.setFixedSize(pixmap.width(), pixmap.height())
        self.patreon_label.mousePressEvent = self.open_patreon_Link
        self.patreon_label.setCursor(Qt.CursorShape.PointingHandCursor)# ｶｰｿﾙを設定
        self.patreon_label.enterEvent = self.patreon_label_enterEvent
        self.patreon_label.leaveEvent = self.patreon_label_leaveEvent
        # Patreonﾗﾍﾞﾙ-----------------------------------

        self.setWindowTitle(SET_WINDOW_TITLE)

        # QPushButtonを作成して､ﾌｫﾝﾄ名をprintする
        button = QPushButton(shige_tr.OK)
        button.clicked.connect(self.handle_button_clicked)
        button.clicked.connect(self.hide)
        button.setFixedWidth(100)

        button2 = QPushButton(shige_tr.Cancel)
        button2.clicked.connect(self.cancelSelect)
        button2.clicked.connect(self.hide)
        button2.setFixedWidth(100)


        button4 = QPushButton("👍️RateThis")
        button4.clicked.connect(lambda: openLink(RATE_THIS_URL))
        # button4.clicked.connect(self.hide)
        button4.setStyleSheet("QPushButton { padding: 2px; }")
        button4.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        button3 = QPushButton("💖Become a patron")
        button3.clicked.connect(lambda: openLink(PATREON_LINK_URL))
        # button3.clicked.connect(self.hide)
        button3.setStyleSheet("QPushButton { padding: 2px; }")
        button3.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        button5 = QPushButton("❔️ Wiki ")
        button5.clicked.connect(lambda: openLink(
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html"))
        button5.setStyleSheet("QPushButton { padding: 2px; }")
        button5.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        report_button = QPushButton("🚨Report")
        report_button.clicked.connect(lambda: openLink(
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#report-a-problem-or-request"))
        report_button.setStyleSheet("QPushButton { padding: 2px; }")
        report_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)


        # add-lineEdit---------------------
        random_prompt_label = self.create_line_edits_and_labels(
            "random_prompt", self.random_prompt, "b_name", 0)

        self.more_info = config["more_info"]
        more_info_label = self.create_line_edits_and_labels(
            "more_info", self.more_info, "b_name",1)

        self.baby_explanation_label = self.create_line_edits_and_labels(
            "baby_explanation",self.baby_explanation, "b_name",2)
        self.word_origin_label = self.create_line_edits_and_labels(
            "word_origin",self.word_origin, "b_name",3)
        self.make_joke_label = self.create_line_edits_and_labels(
            "make_joke",self.make_joke, "b_name",4)
        self.history_label = self.create_line_edits_and_labels(
            "history",self.history, "b_name",5)
        self.synonym_label = self.create_line_edits_and_labels(
            "synonym",self.synonym, "b_name",6)
        self.mnemonic_label = self.create_line_edits_and_labels(
            "mnemonic",self.mnemonic, "b_name",7)

        exclusion_list_label = self.create_line_edits_and_labels(
            "exclusion_list",self.exclusion_list, shige_tr.Exclude_Note)

        self.i_am_studying_label = self.create_line_edits_and_labels(
            "i_am_studying",self.i_am_studying, shige_tr.Prefix + CURLY_BRACES )
        self.language_label = self.create_line_edits_and_labels(
            "language",self.language, shige_tr.Translate + CURLY_BRACES)

        self.Enter_Short_cut_Key_label = self.create_line_edits_and_labels(
            "Enter_Short_cut_Key", self.Enter_Short_cut_Key, shige_tr.send_prompt)

        self.AI_shortcut_key_label = self.create_line_edits_and_labels(
            "AI_shortcut_key", self.AI_shortcut_key, shige_tr.Open_Sidebar)

        self.Priority_tag_list_label = self.create_line_edits_and_labels(
            "Priority_tag_list", self.Priority_tag_list, shige_tr.Tags)

        self.Priority_Fields_list_label = self.create_line_edits_and_labels(
            "Priority_Fields_list", self.Priority_Fields_list, shige_tr.Priority_Fields)


        # # add-lineEdit---------------------
        # random_prompt_label = self.create_line_edits_and_labels(
        #     "random_prompt", self.random_prompt, "default")

        # self.more_info = config["more_info"]
        # more_info_label = self.create_line_edits_and_labels(
        #     "more_info", self.more_info, "more")

        # self.baby_explanation_label = self.create_line_edits_and_labels(
        #     "baby_explanation",self.baby_explanation, "baby")
        # self.word_origin_label = self.create_line_edits_and_labels(
        #     "word_origin",self.word_origin, "origin")
        # self.make_joke_label = self.create_line_edits_and_labels(
        #     "make_joke",self.make_joke, "joke")
        # self.history_label = self.create_line_edits_and_labels(
        #     "history",self.history, "history")
        # self.synonym_label = self.create_line_edits_and_labels(
        #     "synonym",self.synonym, "synonym")
        # self.mnemonic_label = self.create_line_edits_and_labels(
        #     "mnemonic",self.mnemonic, "mnemonic")

        # exclusion_list_label = self.create_line_edits_and_labels(
        #     "exclusion_list",self.exclusion_list,"Exclude Note")

        # self.i_am_studying_label = self.create_line_edits_and_labels(
        #     "i_am_studying",self.i_am_studying,"Prefix")
        # self.language_label = self.create_line_edits_and_labels(
        #     "language",self.language,"Suffix")


        # add-checkBox---------------------

        # toggle 1
        self.is_i_am_studying_label = self.create_checkbox(shige_tr.Use_Prefix, "is_i_am_studying")
        self.change_Language_label = self.create_checkbox(shige_tr.Use_Translate, "change_Language")

        # toggle 2
        self.start_up_label = self.create_checkbox(
            shige_tr.auto_open_sidebar_when_start_anki,"start_up")
        # self.start_up_label.setEnabled(False)


        self.add_gpt_to_the_top_toolbar_label = self.create_checkbox(
            shige_tr.add_ai_icon_button_to_the_top_toolbar, "add_gpt_to_the_top_toolbar")
        # self.input_text_label = self.create_checkbox(
        #     shige_tr.auto_input_prompts, "input_text")
        self.submit_text_label = self.create_checkbox(
            shige_tr.auto_send_prompts, "submit_text")

        self.no_auto_press_send_button
        self.no_auto_press_send_button_label = self.create_checkbox(
            "Auto input text but do not auto send", "no_auto_press_send_button")

        self.auto_read_aloud_label = self.create_checkbox(
            "Auto-read aloud (for ChatGPT only)", "auto_read_aloud")


        self.submit_text_label.setStyleSheet(qtip_style)
        self.submit_text_label.setToolTip(shige_tr.check_box_tooltip)

        self.hide_the_sidebar_on_the_answer_screen_label = self.create_checkbox(
            shige_tr.auto_hide_sidebar_on_review_questions, "hide_the_sidebar_on_the_answer_screen")

        # add-spinBox--------------------
        # self.current_card_values_label,self.current_card_values_spinbox = self.create_spinbox(
        #     "label_text", 0, 100, self.current_card_values, 70, 0, 1, "Attribute_name")

        # ﾎﾞﾘｭｰﾑｺﾝﾄﾛｰﾙ用のｽﾗｲﾀﾞｰを作成 ==========================================
        # self.volume_label, self.volume_slider = self.create_slider(
        #     "label_text", 0.0, 1.0, self.volume, 300, 0.1, "Attribute_name")

        self.Custom_Ai_label = self.create_checkbox(
        "Enable Custom AI URL(Need restart option)", "Custom_Ai")

        self.Custom_AI_URL_label = self.create_line_edits_and_labels(
            "Custom_AI_URL",self.Custom_AI_URL, "CustomAiUrl")


        self.effect_volume_label, self.effect_volume_slider = self.create_slider(
            "Effect Volume", 0.0, 1.0, self.effect_volume, 300, 0.1, "effect_volume")


        self.image_width
        image_width_label, image_width_spinbox =  self.create_spinbox(
            "[ Paste Image Width ]", 0, 9999, self.image_width, 70, 0, 1, "image_width")


        # 全体設定1 ================================
        tab_widget = CustomQTabWidget(self)


        #============================================
        # 各ﾀﾌﾞのﾚｲｱｳﾄを作成
        #============================================

        # theme tab===========================================
        theme_layout = QVBoxLayout()

        theme_HBox_layout = QHBoxLayout()
        theme_HBox_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 左寄せに設定

        # theme_layout.addWidget(self.create_separator())#-------------

        # theme_layout.addWidget(QLabel(f"<b>[ {shige_tr.Prompts} ]</b>" + CURLY_BRACES))
        theme_layout.addWidget(
            WikiQLabel(f"<b>[ {shige_tr.Prompts} ]</b>" + CURLY_BRACES,
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#prompts-tab"))
        
        theme_layout.addLayout(random_prompt_label)
        theme_layout.addLayout(more_info_label)

        theme_layout.addLayout(self.baby_explanation_label)
        theme_layout.addLayout(self.word_origin_label)
        theme_layout.addLayout(self.make_joke_label)
        theme_layout.addLayout(self.history_label)
        theme_layout.addLayout(self.synonym_label)
        theme_layout.addLayout(self.mnemonic_label)

        theme_layout.addStretch(1)
        tab_theme = CustomWidget()
        tab_theme.setLayout(theme_layout)

        # =================================================
        card_layout1 = QVBoxLayout()

        # card_layout1.addWidget(QLabel(f"<b>[ AI ]</b>"))
        card_layout1.addWidget(
            WikiQLabel("[ AI ]",
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#ai--chatgpt-googlegemini-bingchat"))


        if config["Custom_Ai"] and CUSTOM_AI not in THEMES:
            THEMES.append(CUSTOM_AI)

        card_layout1.addLayout(self.create_radio_buttons_from_themes(THEMES))

        card_layout1.addWidget(self.create_separator())#----------------

        card_layout1.addWidget(WikiQLabel(f"<b>[ Custom AI ]</b>",
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#enable-custom-ai-url"))


        card_layout1.addWidget(self.Custom_Ai_label)
        card_layout1.addLayout(self.Custom_AI_URL_label)

        card_layout1.addWidget(self.create_separator())#----------------

        # card_layout1.addWidget(QLabel(f"<b>[ {shige_tr.Translate} ]</b>"))
        card_layout1.addWidget(WikiQLabel(f"<b>[ {shige_tr.Translate} ]</b>",
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#translate"))

        card_layout1.addWidget(self.change_Language_label)
        card_layout1.addLayout(self.language_label)


        random_prompt_lang = config["language"]
        selected_prompt_lang = random.choice(random_prompt_lang)
        lang = shige_tr.lang
        if '{}' in selected_prompt_lang:
            selected_prompt_lang = selected_prompt_lang.replace('{}', lang if lang else "")
            selected_prompt_lang = f" {shige_tr.Result} -> " + selected_prompt_lang
        card_layout1.addWidget(QLabel(selected_prompt_lang))

        card_layout1.addWidget(self.create_separator())#----------------

        image_width_box = QHBoxLayout()
        image_width_box.addWidget(image_width_label)
        image_width_box.addWidget(image_width_spinbox)
        image_width_box.addStretch()
        card_layout1.addLayout(image_width_box)

        card_layout1.addStretch(1)
        tab_Card = CustomWidget()
        tab_Card.setLayout(card_layout1)

        # =================================================
        timer_layout2 = QVBoxLayout()


        timer_layout2.addWidget(WikiQLabel(f"<b>[ {shige_tr.Exclude_Note} ]</b>",
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#exclude-tab"))


        timer_layout2.addLayout(exclusion_list_label)

        timer_layout2.addStretch(1)
        tab_Timer = CustomWidget()
        tab_Timer.setLayout(timer_layout2)

        # sound_layout tab =================================================
        sound_layout = QVBoxLayout()

        # sound_layout.addWidget(QLabel(f"<b>[ {shige_tr.Sidebar} ]</b>"))
        sound_layout.addWidget(WikiQLabel(f"<b>[ {shige_tr.Sidebar} ]</b>",
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#ai-sidebar-options"))

        sound_layout.addWidget(self.start_up_label)
        sound_layout.addWidget(self.hide_the_sidebar_on_the_answer_screen_label)
        sound_layout.addWidget(self.add_gpt_to_the_top_toolbar_label)

        sound_layout.addWidget(self.create_separator())#----------------

        # sound_layout.addWidget(QLabel(f"<b>[ {shige_tr.Auto_Prompt} ]</b>"))
        sound_layout.addWidget(WikiQLabel(f"<b>[ {shige_tr.Auto_Prompt} ]</b>",
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#auto-prompt"))

        # sound_layout.addWidget(self.input_text_label)
        sound_layout.addWidget(self.submit_text_label)
        sound_layout.addWidget(self.no_auto_press_send_button_label)
        sound_layout.addWidget(self.auto_read_aloud_label)

        sound_layout.addWidget(self.create_separator())#----------------

        # sound_layout.addWidget(QLabel(f"<b>[ {shige_tr.Shortcut_Key} ]</b>"))
        sound_layout.addWidget(WikiQLabel(f"<b>[ {shige_tr.Shortcut_Key} ]</b>",
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#shortcut-keys"))



        sound_layout.addLayout(self.Enter_Short_cut_Key_label)
        sound_layout.addLayout(self.AI_shortcut_key_label)

        sound_layout.addWidget(self.create_separator())#----------------

        sound_layout.addWidget(WikiQLabel(self.effect_volume_label,
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#effect-volume"))
        # sound_layout.addWidget(self.effect_volume_label)
        self.effect_volume_label.setVisible(False)
        self.effect_volume_label.deleteLater()
        self.effect_volume_label = None
        
        sound_layout.addWidget(self.effect_volume_slider)

        sound_layout.addStretch(1)
        tab_Sound = CustomWidget()
        tab_Sound.setLayout(sound_layout)

        # tab3 =================================================
        # layout3.addWidget(self.create_separator())#-------------
        other_layout = QVBoxLayout()

        # other_layout.addWidget(QLabel(f"<b>[ {shige_tr.study_content_from_tags} ]</b>"))
        other_layout.addWidget(WikiQLabel(f"<b>[ {shige_tr.study_content_from_tags} ]</b>",
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#tags-tab"))

        other_layout.addWidget(self.is_i_am_studying_label)
        other_layout.addLayout(self.i_am_studying_label)
        other_layout.addWidget(self.create_separator())#----------------
        other_layout.addLayout(self.Priority_tag_list_label)

        other_layout.addStretch(1)

        tab_Other = CustomWidget()
        tab_Other.setLayout(other_layout)


        # tab =================================================
        tab7_layout = QVBoxLayout()

        # tab7_layout.addWidget(QLabel(f"<b>[ {shige_tr.Priority_Fields} ]</b>"))
        tab7_layout.addWidget(WikiQLabel(f"<b>[ {shige_tr.Priority_Fields} ]</b>",
            "https://shigeyukey.github.io/shige-addons-wiki/AnkiTerminator/anki_terminator_00.html#priority-fields-tab"))

        tab7_layout.addLayout(self.Priority_Fields_list_label)


        tab7_layout.addStretch(1)

        tab_tab7 = CustomWidget()
        tab_tab7.setLayout(tab7_layout)
        # tab ｸﾚｼﾞｯﾄ =================================================
        # credit_layout = QVBoxLayout()

        # credit_data_attributes = [
        #                         'credits',
        #                         'patreon',
        #                         'caractor',
        #                         'sound',
        #                         'addons',
        #                         'budle',
        #                         'thankYou',
        #                         ]

        # font = QFont("Times New Roman", 15)
        # # font.setItalic(True)
        # for attribute in credit_data_attributes:
        #     label = QLabel(f'<style>body, a {{ color: white; }}</style><body>{getattr(CreditData, attribute)}</body>')
        #     label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #     label.setFont(font)
        #     label.setOpenExternalLinks(True)
        #     credit_layout.addWidget(label)

        # credit_layout.addStretch(1)

        # # (Credit)ｽｸﾛｰﾙｴﾘｱを作成 ----------------------
        # scroll_area = QScrollArea()
        # scroll_area.setWidgetResizable(True)
        # tab_Credit = EndrollWidget(self,scroll_area)
        # tab_Credit.setLayout(credit_layout)
        # scroll_area.setWidget(tab_Credit)



        # 全体設定2 ================================

        # ﾀﾌﾞｳｨｼﾞｪｯﾄに各ﾀﾌﾞを追加
        tab_widget.addTab(tab_Card, self.TAB_TWO)
        tab_widget.addTab(tab_theme,self.TAB_ONE)
        tab_widget.addTab(tab_Other, self.TAB_FIVE)
        tab_widget.addTab(tab_tab7, self.TAB_SEVEN)
        tab_widget.addTab(tab_Timer,self.TAB_THREE)
        tab_widget.addTab(tab_Sound,self.TAB_FOUR)
        add_change_log_tab(self, tab_widget)
        add_credit_tab(self, tab_widget)
        add_shige_addons_tab(self, tab_widget)


        # 最後のﾀﾌﾞを記憶
        try:
            last_tab_index = self.last_tab
            tab_widget.setCurrentIndex(last_tab_index)
            tab_widget.currentChanged.connect(self.save_current_tab_index)
        except:
            pass


        main_layout = QVBoxLayout()
        main_layout.addWidget(self.patreon_label)
        main_layout.addWidget(tab_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(button)
        button_layout.addWidget(button2)

        button_layout.addStretch()
        button_layout.addWidget(button3)
        button_layout.addWidget(button4)
        button_layout.addWidget(button5)
        button_layout.addWidget(report_button)


        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.adjust_self_size()

        # 全体 ================================
        PYGsound(SOUND_OPEN)
        def on_tab_changed(index): #indexはこのままで良
            PYGsound(SOUND_SELECT)
        tab_widget.currentChanged.connect(on_tab_changed)








    def save_current_tab_index(self,index):
        self.last_tab = index

    # 各AIのﾗｼﾞｵﾎﾞﾀﾝを作成する関数===============
    # def create_radio_buttons_from_themes(self, themes):
    #     layout = QVBoxLayout()
    #     for theme in themes:
    #         radio_button = QRadioButton(theme)
    #         if theme == self.now_AI_type:
    #             radio_button.setChecked(True)
    #         radio_button.toggled.connect(lambda checked, theme=theme: self.update_AI_type(checked, theme))
    #         layout.addWidget(radio_button)
    #     return layout

    def create_radio_buttons_from_themes(self, themes):
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        for index, theme in enumerate(themes, start=1):
            radio_button = QRadioButton(theme)
            if theme == self.now_AI_type:
                radio_button.setChecked(True)
            radio_button.toggled.connect(lambda checked, theme=theme: self.update_AI_type(checked, theme))
            hbox.addWidget(radio_button)
            if index % 5 == 0:
                hbox.addStretch()
                layout.addLayout(hbox)
                hbox = QHBoxLayout()
        if hbox.count() > 0:
            hbox.addStretch()
            layout.addLayout(hbox)
        return layout

    def update_AI_type(self, checked, theme):
        if checked:
            self.now_AI_type = theme
            PYGsound(SOUND_SELECT)
    #============================================


    # ﾃｷｽﾄﾎﾞｯｸｽを作成する関数=========================
    def create_line_edits_and_labels(self, list_attr_name, list_items, b_name, b_index=None):
        main_layout = QVBoxLayout()
        items = list_items if isinstance(list_items, list) else [list_items]
        for i, item in enumerate(items):
            line_edit = QLineEdit(item)
            line_edit.textChanged.connect(lambda text,
                                        i=i,
                                        name=list_attr_name: self.update_list_item(name, i, text))
            line_edit.setMaximumWidth(SET_LINE_EDID_WIDTH)

            if i == 0:
                layout = QHBoxLayout()
                if b_index is not None:
                    b_name_attr = getattr(self, b_name)
                    label_edit = QLineEdit(b_name_attr[b_index])
                    label_edit.textChanged.connect(lambda text,
                                                i=i,
                                                b_name=b_name: self.update_label_item(b_name, b_index, text))
                    label_edit.setFixedWidth(MAX_LABEL_WIDTH)
                    layout.addWidget(label_edit)
                else:
                    label = QLabel(b_name)
                    label.setFixedWidth(MAX_LABEL_WIDTH)
                    layout.addWidget(label)
            else:
                label = QLabel()
                label.setFixedWidth(MAX_LABEL_WIDTH)
                layout = QHBoxLayout()
                layout.addWidget(label)

            line_edit = QLineEdit(item)
            line_edit.textChanged.connect(lambda text,
                                        i=i,
                                        name=list_attr_name: self.update_list_item(name, i, text))
            line_edit.setMaximumWidth(SET_LINE_EDID_WIDTH)
            layout.addWidget(line_edit)
            main_layout.addLayout(layout)
        return main_layout

    def update_label_item(self, b_name, index, text):
        update_label = getattr(self,b_name)
        update_label[index] = text
    def update_list_item(self, list_attr_name, index, text):
        # list_to_update = getattr(self, list_attr_name)
        # list_to_update[index] = text
        list_to_update = getattr(self, list_attr_name)
        if isinstance(list_to_update, list):
            list_to_update[index] = text
        else:
            setattr(self, list_attr_name, text)
    # ===================================================




    # # ﾃｷｽﾄﾎﾞｯｸｽを作成する関数=========================
    # def create_line_edits_and_labels(self, list_attr_name, list_items, label_name):
    #     main_layout = QVBoxLayout()
    #     for i, item in enumerate(list_items):
    #         line_edit = QLineEdit(item)
    #         line_edit.textChanged.connect(lambda text,
    #                                     i=i,
    #                                     name=list_attr_name: self.update_list_item(name, i, text))
    #         line_edit.setMaximumWidth(SET_LINE_EDID_WIDTH)
    #         if i == 0:
    #             label = QLabel(label_name)
    #             label.setFixedWidth(MAX_LABEL_WIDTH)
    #         else:
    #             label = QLabel()
    #             label.setFixedWidth(MAX_LABEL_WIDTH)
    #         layout = QHBoxLayout()
    #         layout.addWidget(label)
    #         layout.addWidget(line_edit)
    #         main_layout.addLayout(layout)
    #     return main_layout
    # # ﾃｷｽﾄﾎﾞｯｸｽを作成する関数(2)
    # def update_list_item(self, list_attr_name, index, text):
    #     list_to_update = getattr(self, list_attr_name)
    #     list_to_update[index] = text
    # # ===================================================

    # def create_line_edits_and_labels(self, list_attr_name, list_items, label_name):
    #     main_layout = QVBoxLayout()
    #     for i, item in enumerate(list_items):
    #         combobox = QComboBox()
    #         combobox.setEditable(True)
    #         combobox.addItems(list_items)
    #         combobox.setCurrentText(item)
    #         combobox.currentTextChanged.connect(lambda text,
    #                                         i=i,
    #                                         name=list_attr_name: self.update_list_item(name, i, text))
    #         combobox.setMaximumWidth(SET_LINE_EDID_WIDTH)
    #         if i == 0:
    #             label = QLabel(label_name)
    #             label.setFixedWidth(MAX_LABEL_WIDTH)
    #         else:
    #             label = QLabel()
    #             label.setFixedWidth(MAX_LABEL_WIDTH)
    #         layout = QHBoxLayout()
    #         layout.addWidget(label)
    #         layout.addWidget(combobox)
    #         main_layout.addLayout(layout)
    #     return main_layout
    # # ﾃｷｽﾄﾎﾞｯｸｽを作成する関数(2)
    # def update_list_item(self, list_attr_name, index, text):
    #     list_to_update = getattr(self, list_attr_name)
    #     list_to_update[index] = text
    # # ===================================================


    def adjust_self_size(self):
        # min_size = self.layout().minimumSize()
        # self.resize(min_size.width(), min_size.height())
        # self.resize(min_size.width(), WIDGET_HEIGHT)
        self.resize(WIDGET_WIDTH, WIDGET_HEIGHT)


    def create_group_box(self):
        group_box = QGroupBox("Advanced")
        group_box.setObjectName("myGroupBox")
        group_box.setStyleSheet("""
            QGroupBox#myGroupBox { font-weight: normal; }
            QGroupBox#myGroupBox::title { color: gray; }
        """)
        group_box.setCheckable(True)
        group_box.setChecked(False)
        card_layout2 = QVBoxLayout()
        group_box.setLayout(card_layout2)
        return group_box, card_layout2


    # --- cancel -------------
    def cancelSelect(self):
        PYGsound(SOUND_CANCEL)
        emoticons = [":-/", ":-O", ":-|"]
        selected_emoticon = random.choice(emoticons)
        tooltip("Canceled " + selected_emoticon)
        self.close()

    # ﾚｲｱｳﾄにｽﾍﾟｰｽを追加する関数=======================
    def add_widget_with_spacing(self,layout, widget):
        hbox = QHBoxLayout()
        hbox.addSpacing(15)  # ｽﾍﾟｰｼﾝｸﾞを追加
        hbox.addWidget(widget)
        hbox.addStretch(1)
        layout.addLayout(hbox)

    # ｾﾊﾟﾚｰﾀを作成する関数=========================
    def create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("border: 1px solid gray")
        return separator
    # =================================================

    # ﾁｪｯｸﾎﾞｯｸｽを生成する関数=======================
    def create_checkbox(self, label, attribute_name):
        checkbox = QCheckBox(label, self)
        checkbox.setChecked(getattr(self, attribute_name))

        def handler(state):
            if state == 2:
                setattr(self, attribute_name, True)
            else:
                setattr(self, attribute_name, False)
            PYGsound(SOUND_SELECT)

        checkbox.stateChanged.connect(handler)
        return checkbox
    #=================================================

    # ｽﾋﾟﾝﾎﾞｯｸｽを作成する関数=========================
    def create_spinbox(self, label_text, min_value,
                                max_value, initial_value, width,
                                decimals, step, attribute_name):
        def spinbox_handler(value):
            value = round(value, 1)
            if decimals == 0:
                setattr(self, attribute_name, int(value))
            else:
                setattr(self, attribute_name, value)
            PYGsound(SOUND_SELECT)

        label = QLabel(label_text, self)
        spinbox = QDoubleSpinBox(self)
        spinbox.setMinimum(min_value)
        spinbox.setMaximum(max_value)
        spinbox.setValue(initial_value)
        spinbox.setFixedWidth(width)
        spinbox.setDecimals(decimals)
        spinbox.setSingleStep(step)
        spinbox.valueChanged.connect(spinbox_handler)
        return label, spinbox
    #=================================================


    # (Volume用)ｽﾗｲﾀﾞｰを作成する関数============================
    def create_slider(self, label_text, min_value, max_value, initial_value, width, step, attribute_name):
        def slider_handler(value):
            # ｽﾗｲﾀﾞｰの値をｽｹｰﾙﾀﾞｳﾝ
            value = round(value * step, 2)
            setattr(self, attribute_name, float(value))
            PYGsound(SOUND_SELECT,value)

        label = QLabel(label_text, self)
        slider = QSlider(Qt.Orientation.Horizontal, self)
        slider.setMinimum(int(min_value * 10))  # ｽｹｰﾙｱｯﾌﾟ
        slider.setMaximum(int(max_value * 10))  # ｽｹｰﾙｱｯﾌﾟ
        slider.setValue(int(initial_value * 10))  # ｽｹｰﾙｱｯﾌﾟ
        slider.setFixedWidth(width)
        slider.setTickInterval(1)
        slider.valueChanged.connect(slider_handler)
        return label, slider
    #===============================================


    # ------------ patreon label----------------------
    def load_and_process_image(self, image_path):
        self.pixmap = QPixmap(image_path)
        self.pixmap = self.pixmap.scaledToWidth(SET_SCALEDTOWIDTH, Qt.TransformationMode.SmoothTransformation)

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.pixmap.rect()), 10, 10)  # 10は角の丸みの大きさ
        rounded_pixmap = QPixmap(self.pixmap.size())
        rounded_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.end()
        self.pixmap = rounded_pixmap

    def patreon_label_enterEvent(self, event):
        addon_path = dirname(__file__)
        patreon_banner_hover_path = join(addon_path, PATREON_BANNER_JPG)
        self.load_and_process_image(patreon_banner_hover_path)
        self.patreon_label.setPixmap(self.pixmap)
        PYGsound(SOUND_SELECT)

    def patreon_label_leaveEvent(self, event):
        self.load_and_process_image(self.addon_banner_image)
        self.patreon_label.setPixmap(self.pixmap)
        PYGsound(SOUND_SELECT)
    # ------------ patreon label----------------------

    #-- open patreon link-----
    def open_patreon_Link(self,url):
        openLink(PATREON_LINK_URL)
        PYGsound(SOUND_OPENLINK)

    #------------spinbox-----------------


    def update_shortcuts(self):
        from ..add_menu import menu_action
        from ..dock_web_view import web_shortcut
        if menu_action is not None:
            menu_action.setShortcut(QKeySequence(self.AI_shortcut_key))
        if web_shortcut is not None:
            web_shortcut.setShortcut(QKeySequence(self.Enter_Short_cut_Key))
            # web_shortcut.setKey(QKeySequence(self.Enter_Short_cut_Key))


    def handle_button_clicked(self):
        PYGsound(SOUND_OK)
        self.save_config_fontfamiles()
        from ..dock_web_view import dock_content
        if dock_content is not None:
            dock_content.update_button_names()
            dock_content.change_AI_type(False)
            dock_content.checkbox.setChecked(self.submit_text)
        self.update_shortcuts()

        emoticons = [":-)", ":-D", ";-)"]
        selected_emoticon = random.choice(emoticons)
        tooltip("Changed setting " + selected_emoticon)

    def save_config_fontfamiles(self):
        config = mw.addonManager.getConfig(__name__)

        # button_name_list
        config["button_name"] = self.b_name

        # list
        config["random_prompt"] = self.random_prompt
        config["exclusion_list"] = self.exclusion_list
        config["more_info"] = self.more_info
        config["baby_explanation"] = self.baby_explanation
        config["word_origin"] = self.word_origin
        config["make_joke"] = self.make_joke
        config["history"] = self.history
        config["synonym"] = self.synonym
        config["mnemonic"] = self.mnemonic

        # toggle
        config["is_i_am_studying"] = self.is_i_am_studying
        config["change_Language"] = self.change_Language
        config["start_up"] = self.start_up
        config["add_gpt_to_the_top_toolbar"] = self.add_gpt_to_the_top_toolbar
        # config["input_text"] = self.input_text
        config["submit_text"] = self.submit_text
        config["hide_the_sidebar_on_the_answer_screen"] = self.hide_the_sidebar_on_the_answer_screen

        # no list
        config["i_am_studying"] = self.i_am_studying
        config["language"] = self.language

        # list 3
        config["Priority_tag_list"] = self.Priority_tag_list
        config["Priority_Fields_list"] = self.Priority_Fields_list

        # AI type
        config["now_AI_type"] = self.now_AI_type

        # shortcut keys
        config["Enter_Short_cut_Key"] = self.Enter_Short_cut_Key
        config["AI_shortcut_key"] = self.AI_shortcut_key

        config["last_tab"] = self.last_tab

        # custom Ai
        config["Custom_Ai"] = self.Custom_Ai
        config["Custom_AI_URL"] = self.Custom_AI_URL

        config["EffectVolume"] = self.effect_volume
        config["auto_read_aloud"] = self.auto_read_aloud

        config["image_width"] = self.image_width

        # no auto send
        config["no_auto_press_send_button"] = self.no_auto_press_send_button


        mw.addonManager.writeConfig(__name__, config)

        # 設定したconfigをすべてﾌﾟﾘﾝﾄ
        print("--------[config]--------")
        def print_config():
            config_text = ""
            for key, value in config.items():
                config_text += f"{key}: {value}<br>"
            return config_text
        print("--------[config]--------")

        # self.show_custom_massage_box()
        # --------------show message box-----------------
    def show_custom_massage_box(self):
        try:
            some_restart_anki =tr.preferences_some_settings_will_take_effect_after()
        except:
            some_restart_anki ="Some settings will take effect after you restart Anki."

        pixmap = QPixmap(self.icon_path)
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.NoIcon)
        msg_box.setIconPixmap(pixmap)
        # msg_box.setText(some_restart_anki+"<br><br>"+print_config())
        msg_box.setText(some_restart_anki)
        msg_box.setWindowTitle(SET_WINDOW_TITLE)
        msg_box.setWindowIcon(QIcon(self.icon_path))
        countdown = [3]

        def update_text():
            countdown[0] -= 1
            if countdown[0] > 0:
                button.setText(f"{countdown[0]}")
            else:
                msg_box.close()
        button = msg_box.addButton(QMessageBox.StandardButton.Ok)
        button.setText(f"{countdown[0]}")
        timer = QTimer()
        timer.timeout.connect(update_text)
        timer.start(1000)

        QTimer.singleShot(3000, msg_box.close)
        try:
            msg_box.exec()
        except:
            try:
                msg_box.exec_()
            except:
                showInfo(some_restart_anki, title=SET_WINDOW_TITLE)

    def checkNightMode(self):
        try:
            from anki import version as anki_version
            old_anki = tuple(int(i) for i in anki_version.split(".")) < (2, 1, 20)
            if old_anki:
                return False
            else:
                from aqt.theme import theme_manager
                return theme_manager.night_mode
        except:
            return False


    def resizeEvent(self, event):
        size = event.size()
        print(f"Width: {size.width()}, Height: {size.height()}")
        super().resizeEvent(event)


#----------画像のﾗﾝﾀﾞﾑ選択-----------
def get_mediaFile_path(name):
    addon_path =  os.path.dirname(os.path.dirname(__file__))
    audio_folder = join(addon_path,name)
    return audio_folder

# -----------効果音の追加--------------
from .BGM_player import pyg_play_sound

def get_path(name):
    addon_path = dirname(__file__)
    parentFoldere = SOUND_SYSTEM
    audio_folder = join(addon_path,parentFoldere, name)
    return audio_folder

def PYGsound(sound_name,volume=None):
    config = mw.addonManager.getConfig(__name__)
    if not volume == None:
        EffectVolume = volume
    else:
        EffectVolume = config["EffectVolume"]
    pyg_play_sound(get_path(sound_name), EffectVolume,False,True)

# -----------効果音の追加--------------


def set_this_addon_Config():# __init__で使う
    font_viewer = SetPopupConfig(mw)
    try:
        font_viewer.exec()
    except:
        font_viewer.exec_()


class CustomWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def checkNightMode(self):
        try:
            from anki import version as anki_version
            old_anki = tuple(int(i) for i in anki_version.split(".")) < (2, 1, 20)
            if old_anki:
                return False
            else:
                from aqt.theme import theme_manager
                return theme_manager.night_mode
        except:
            return False


class CustomQTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUsesScrollButtons(False)
        self.setElideMode(Qt.TextElideMode.ElideNone)

        if not parent.check_Anki_Style_existence:
            self.setStyleSheet("background-color: transparent;")

    def checkNightMode(self):
        try:
            from anki import version as anki_version
            old_anki = tuple(int(i) for i in anki_version.split(".")) < (2, 1, 20)
            if old_anki:
                return False
            else:
                from aqt.theme import theme_manager
                return theme_manager.night_mode
        except:
            return False


# ============== [ config ] =================


# from .config.PopUpAnkiConfig import SetAnkiPopupConfig

def shige_config_setup():
    # ----- add-onのconfigをｸﾘｯｸしたら設定ｳｨﾝﾄﾞｳを開く -----
    def add_config_button():
        mw.addonManager.setConfigAction(__name__, set_this_addon_Config)
        # ----- ﾒﾆｭｰﾊﾞｰに追加 -----
        addon_action = QAction(f"{SET_WINDOW_TITLE} Settings", mw)
        qconnect(addon_action.triggered, set_this_addon_Config)

        # global this_addon_menu
        # if this_addon_menu == None:
        #     this_addon_menu = QMenu(SET_WINDOW_TITLE, mw)
        # this_addon_menu.addAction(addon_action)
        # global anki_terminator_menu
        # anki_terminator_menu = QMenu(SET_WINDOW_TITLE, mw)
        # mw.form.menuTools.addMenu(anki_terminator_menu)
        from ..make_manu import get_anki_terminator_menu
        get_anki_terminator_menu().addAction(addon_action)

    gui_hooks.main_window_did_init.append(add_config_button)
