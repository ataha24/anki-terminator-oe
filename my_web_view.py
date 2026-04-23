# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

from aqt import  QDialog, QIcon, QSize, QUrl, QVBoxLayout, QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineView, Qt, mw
from aqt.webview import AnkiWebView
from os.path import join, dirname
from aqt import QTimer, Qt, gui_hooks,mw


did_modal_hide_count = False
modalCheacktimer = QTimer()
# ｳｨﾝﾄﾞｳを作成

class MyWebPage(QWebEnginePage):
    # ﾊﾟｿｺﾝのﾃﾞﾌｫﾙﾄのﾌﾞﾗｳｻﾞで開かれてしまう場合､
    # QWebEnginePageのcreateWindow関数をｵｰﾊﾞｰﾗｲﾄﾞする必要がある
    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = AnkiWebView(title="My Web Page")
        new_webview.setPage(MyWebPage(new_webview))
        return new_webview.page()


class ResizableWebView(QDialog):
    def __init__(self,name,url):
        super().__init__()

        self.cookie_profile = QWebEngineProfile("my_profile")
        # profile = QWebEngineProfile.defaultProfile() # ﾃﾞﾌｫﾙﾄのﾌﾟﾛﾌｧｲﾙ名
        self.cookie_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        browser_storage_folder = join(dirname(__file__), "cookie_data")
        self.cookie_profile.setPersistentStoragePath(browser_storage_folder)

        self.setWindowTitle(name)
        self.setMinimumSize(QSize(300, 300))

        self.webview = QWebEngineView()
        # self.webview = AnkiWebView()

        # ｸﾘｯﾌﾟﾎﾞｰﾄﾞにｺﾋﾟｰ可能にする
        settings = self.cookie_profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)

        webpage = QWebEnginePage(self.cookie_profile, self.webview)
        self.webview.setPage(webpage)
        self.webview.load(QUrl(url))

        layout = QVBoxLayout(self)
        layout.addWidget(self.webview)
        layout.setContentsMargins(1, 1, 1, 1)

        self.setLayout(layout)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # closeEventをﾌｯｸしてｵﾌﾞｼﾞｪｸﾄを削除しないようにする
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        # ｱｲｺﾝを設定する
        addon_path = dirname(__file__)
        icon_path = join(addon_path, r'ChatGPT_logo.png')
        self.setWindowIcon(QIcon(icon_path))

    def resizeEvent(self, event):
        self.webview.resize(self.width(), self.height())

    # ｳｨﾝﾄﾞｳを非表示にする
    def hideEvent(self, event):
        self.hide()

    # ｳｨﾝﾄﾞｳを再表示する
    def showEvent(self, event):
        self.show()

    def closeEvent(self,*args,**kwargs):
        global did_modal_hide_count
        did_modal_hide_count = False
        self.hide()
        global modalCheacktimer
        if modalCheacktimer.isActive():
            modalCheacktimer.stop()

    def close_dialog(self,*args,**kwargs):
        try:
            global did_modal_hide_count
            did_modal_hide_count = False
            self.webview.page().deleteLater()
            self.cookie_profile.deleteLater()
            self.close()
            global modalCheacktimer
            if modalCheacktimer.isActive():
                modalCheacktimer.stop()
        except:
            return

def Web_view(name, url):
    for widget in mw.app.topLevelWidgets():
        if isinstance(widget, ResizableWebView) and widget.windowTitle() == name:
            # widget.webview.setUrl(QUrl(url))
            widget.activateWindow()
            widget.raise_()
            # ｳｨﾝﾄﾞｳが非表示の場合､再度表示する
            widget.showNormal()
            modal_Cheack_timer()
            return

    mw.web_dialog = ResizableWebView(name, url)
    # ｳｨﾝﾄﾞｳﾌﾗｸﾞの設定
    mw.web_dialog.setWindowFlags(mw.web_dialog.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)

    mw.web_dialog.show()
    modal_Cheack_timer()

    # 初回のみgui_hooksに追加する
    if not getattr(Web_view, 'counter', None):
        Web_view.counter = 1
        gui_hooks.profile_will_close.append(mw.web_dialog.close_dialog)


# ﾓｰﾀﾞﾙｩｲﾝﾄﾞｳが起動中のみ非表示にする

# did_modal_hide_count = False
def modalWindowhide():
    global did_modal_hide_count
    # print(did_modal_hide_count)
    name = "ChatGPT"
    for window in mw.app.topLevelWidgets():
        if window.isVisible() and window.windowModality() == Qt.WindowModality.ApplicationModal:
            for widget in mw.app.topLevelWidgets():
                if isinstance(widget, ResizableWebView) and widget.windowTitle() == name:
                    if widget.isVisible():
                        widget.hide()
                        did_modal_hide_count = True
                        return
                    else:
                        return
        elif did_modal_hide_count:
            modal_visible = False
            for window_2 in mw.app.topLevelWidgets():
                if window_2.isVisible() and window_2.windowModality() == Qt.WindowModality.ApplicationModal:
                    modal_visible = True
                    break
            if not modal_visible:
                for widget_2 in mw.app.topLevelWidgets():
                    if isinstance(widget_2, ResizableWebView) and widget_2.windowTitle() == name:
                        if widget_2.isHidden():
                            widget_2.activateWindow()
                            widget_2.raise_()
                            widget_2.showNormal()
                            did_modal_hide_count = False
                            return

# modalCheacktimer = QTimer()
def modal_Cheack_timer():
    global modalCheacktimer
    if not modalCheacktimer.isActive():
        # modalCheacktimer = mw.modalCheacktimer = QTimer()
        modalCheacktimer.setInterval(1000)  # 1000ﾐﾘ秒 = 1秒
        modalCheacktimer.timeout.connect(modalWindowhide)
        modalCheacktimer.start()

