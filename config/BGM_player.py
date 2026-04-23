


import os
import pyglet
from aqt.qt import QTimer
import random
from aqt import QObject, mw

pyglet_sound_play_01 = None
pyglet_sound_play_02 = None
pyglet_sound_play_03 = None

# pygletで音声を再生
class play_pyglet_bgm(QObject):
    pyglet_bgm_sound = None
    pyglet_qtimer = None
    Enable_BGM = True

    def __init__(self,parent=None):
        super().__init__(parent)
        self.pyglet_bgm_sound = None
        self.pyglet_qtimer = QTimer(self)  # selfを親として指定
        self.Enable_BGM = True
        pass

    def play_sound_and_BGM(self, name=None, Volume=0.1, loop=True, folder=False):
        if name is None:
            return

        self.audio_folder = name
        self.player = pyglet.media.Player()
        self.pyglet_bgm_sound = self.player
        self.player.volume = Volume


        if folder:
            if os.path.isdir(self.audio_folder):
                # mp3, wav, ogg ﾌｧｲﾙのみを含む
                audioName_list = [f for f in os.listdir(self.audio_folder)
                                if os.path.isfile(os.path.join(self.audio_folder, f))
                                and f.endswith(('.mp3', '.wav', '.ogg'))]
                if not audioName_list:
                    return

                audio_name = random.choice(audioName_list)
                self.audio_path = os.path.join(self.audio_folder, audio_name)
            else:
                return
        else:
            self.audio_path = name

        BGM_do_it = pyglet.media.load(self.audio_path, streaming=False)
        self.player.queue(BGM_do_it)
        self.player.loop = loop

        self.player.play()

        # pygletとQtのｲﾍﾞﾝﾄﾙｰﾌﾟの競合をQtimerで回避
        self.pyglet_qtimer.timeout.connect(self.tick)
        self.pyglet_qtimer.start(200)  # 200ﾐﾘ秒ごとにtick()を呼び出す

    def tick(self):
        if self.Enable_BGM:
            if self.player.playing:
                pyglet.clock.tick()
                pyglet.app.platform_event_loop.dispatch_posted_events()
            else:
                self.pyglet_qtimer.stop()

    def restart_BGM(self):
        self.Enable_BGM = True

    def stop_BGM_2(self):
        self.Enable_BGM = False

        if self.pyglet_bgm_sound == None:
            return
        else:
            self.pyglet_bgm_sound.pause()
            self.pyglet_bgm_sound.delete()
        try:
            self.pyglet_qtimer.stop()
            # pyglet.app.exit()
        except:
            pass

pyglet_sounds = [None, None, None]
def pyg_play_sound(name, volume, loop, folder):
    # return
    """ for Sound Effect """
    global pyglet_sounds
    new_sound = play_pyglet_bgm(mw)
    # ﾘｽﾄに音声が3つある場合は､最初の音声を削除
    if None not in pyglet_sounds:
        pyglet_sounds.pop(0)
    pyglet_sounds.append(new_sound)
    new_sound.play_sound_and_BGM(name, volume, loop, folder)


def pyg_play_sound2(name,volume,loop,folder):
    # return
    """ for BGM """
    global pyglet_sound_play_02
    if pyglet_sound_play_02 == None:
        pyglet_sound_play_02 = play_pyglet_bgm(mw)
    else:
        pyglet_sound_play_02.pyglet_bgm_sound.pause()
    pyglet_sound_play_02.play_sound_and_BGM(name,volume,loop,folder)

def pyg_play_sound3(name,volume,loop,folder):
    # return
    """ ﾎﾟﾓﾄﾞｰﾛ用のｻｳﾝﾄﾞ
    効果音が重なるとｶﾞﾍﾞｰｼﾞｺﾚｸｼｮﾝされ長いｻｳﾝﾄﾞは途中で終わる"""
    global pyglet_sound_play_03
    if pyglet_sound_play_03 == None:
        pyglet_sound_play_03 = play_pyglet_bgm(mw)
    pyglet_sound_play_03.play_sound_and_BGM(name,volume,loop,folder)


def reset_globals():
    global pyglet_sounds, pyglet_sound_play_01, pyglet_sound_play_02, pyglet_sound_play_03
    if pyglet_sound_play_01 != None:
        pyglet_sound_play_01.stop_BGM_2()
        pyglet_sound_play_01 = None
    if pyglet_sound_play_02 != None:
        pyglet_sound_play_02.stop_BGM_2()
        pyglet_sound_play_02 = None
    if pyglet_sound_play_03 != None:
        pyglet_sound_play_03.stop_BGM_2()
        pyglet_sound_play_03 = None
    for i in range(len(pyglet_sounds)):
        if pyglet_sounds[i] != None:
            pyglet_sounds[i].stop_BGM_2()
            pyglet_sounds[i] = None
