# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>



from aqt import mw

THEMES = []

ADDON_NAME = "AnkiTerminator"

ADDON_TITLE = "Anki Terminator"
ADDON_TITLE_2 = "Anki Terminator (Created by Shige)"
SUB_TITLE = "ChatGPT for Anki Sidebar, Google Bard, Bing Chat"

CHAT_GPT = "Chat_GPT"
THEMES.append(CHAT_GPT)

GOOGLE_BARD = "Google_Bard"
THEMES.append(GOOGLE_BARD)

BING_CHAT = "Bing_Chat"
THEMES.append(BING_CHAT)

CLAUDE = "Claude"
CLAUDE_URL = "https://claude.ai/chat/"
THEMES.append(CLAUDE)

PERPLEXITY= "perplexity"
PERPLEXITY_URL = "https://www.perplexity.ai/"
THEMES.append(PERPLEXITY)

DEEP_SEEK= "DeepSeek"
DEEP_SEEK_URL = "https://chat.deepseek.com/"
THEMES.append(DEEP_SEEK)

IMAGE_FX = "Image_FX"
IMAGE_FX_URL = "https://labs.google/fx/tools/image-fx"
# THEMES.append(IMAGE_FX)

GROK_AI = "Grok_AI"
GROK_AI_URL = "https://grok.com/"
GROK_LOGO = "Grok_logo.png"
THEMES.append(GROK_AI)

DUCK_AI = "Duck_AI"
DUCK_AI_URL = "https://duckduckgo.com/aichat"
DUCK_AI_LOGO = "The_DuckDuckGo_Duck.png"
THEMES.append(DUCK_AI)

OPEN_EVIDENCE = "Open_Evidence"
OPEN_EVIDENCE_URL = "https://www.openevidence.com"
THEMES.append(OPEN_EVIDENCE)



CUSTOM_AI = "Custom_Ai"

WITHOUT_THEMES = []

COOKIE_DATA = "cookie_data"
USER_FILES = "user_files"

check_box_tooltip = "Automatically send default prompt after show card answer"

LABEL_TEXT = "AI"
LABEL_ID = "shige_chatGPT"
LABEL_PYCMD = "shige_chatGPT_toolbar_clicked"
LABEL_INDEX = 5

HIDE_HIGHT = 10

NOW_LOADING = r'NowLoading.png'
SHOW_ANSWER_PNG = r'ShowAnswer.png'

CHAT_GPT_LOGO = r'ChatGPT_logo.png'
GOOGLE_BARD_LOGO = r'Google_Bard_logo.png'
BING_CHAT_LOGO = r'Bing_Chat_Icon.png'

DEEP_SEEK_LOGO = "deepseek.png"
PERPLEXITY_LOGO = "perplexity.png"
CLAUDE_LOGO = "Claude.png"
IMAGE_FX_LOGO = "imageFX.png"

CUSTOM_LOGO = r'Custom_logo.png'




def update_theme():
    config = mw.addonManager.getConfig(__name__)
    try:
        # WITHOUT_THEMESの中にあるﾃｰﾏを除外
        themes_without_excluded = [theme for theme in THEMES if theme not in WITHOUT_THEMES]
        current_index = themes_without_excluded.index(config["now_AI_type"])
        config["now_AI_type"] = themes_without_excluded[(current_index + 1) % len(themes_without_excluded)]
    except:
        config["now_AI_type"] = CHAT_GPT
    mw.addonManager.writeConfig(__name__, config)

