# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

# pygletをimportする

import sys               # sysﾓｼﾞｭｰﾙをｲﾝﾎﾟｰﾄ
import pathlib           # pathlibﾓｼﾞｭｰﾙをｲﾝﾎﾟｰﾄ
import importlib.util    # importlib.utilﾓｼﾞｭｰﾙをｲﾝﾎﾟｰﾄ


# https://forums.ankiweb.net/t/best-practice-for-add-ons-using-third-party-packages/1585/2

def load_pyglet_and_setup():
    # pygletﾓｼﾞｭｰﾙがまだ読み込まれていない場合にのみ実行する
    if 'pyglet' not in sys.modules:
        # このｱﾄﾞｵﾝのﾙｰﾄﾃﾞｨﾚｸﾄﾘを取得する
        addon_root = pathlib.Path(__file__).resolve().parent
        # pygletのｿｰｽﾌｧｲﾙのﾊﾟｽを作成する
        pyglet_source = addon_root / 'bundle' / 'pyglet' / '__init__.py'
        # pygletのspecｵﾌﾞｼﾞｪｸﾄを取得する
        spec = importlib.util.spec_from_file_location('pyglet', pyglet_source)
        # pygletのﾓｼﾞｭｰﾙｵﾌﾞｼﾞｪｸﾄを生成する
        module = importlib.util.module_from_spec(spec)
        # sys.modulesにpygletのﾓｼﾞｭｰﾙｵﾌﾞｼﾞｪｸﾄを追加する
        sys.modules['pyglet'] = module
        # pygletをﾛｰﾄﾞする
        spec.loader.exec_module(module)

        load_pyglet_and_setup_2()

def load_pyglet_and_setup_2():
    # ------- pyglet ----------
    # WARNING:ｲﾍﾞﾝﾄﾙｰﾌﾟがQtと競合してｸﾗｯｼｭします
    # pygletｳｨﾝﾄﾞｳ､runは使用できません

    # pygletをｲﾝﾎﾟｰﾄする
    import pyglet

    # Pyglet が開いている gl ｺﾝﾃｷｽﾄを初期化しないようにする
    # ｼｬﾄﾞｰｳｨﾝﾄﾞｳを使わない
    pyglet.options['shadow_window'] = False
    # Openglのﾃﾞﾊﾞｯｸﾞﾓｰﾄﾞを有効にするかどうか
    pyglet.options['debug_gl'] = False
    # NOTE: Openglを無効にしないとpyqtと競合し起動時にｸﾗｯｼｭしやすい

    # ------- pyglet ----------

    # from .pyglet_bgm import bgm_player
    # #Anki を閉じるときにｱﾌﾟﾘの実行を終了する
    # gui_hooks.profile_will_close.append(bgm_player.stop_BGM)
    # gui_hooks.profile_will_close.append(pyglet.app.exit)
