
from ..path_manager import ADDON_TITLE

def clink(name, text,url=None):
    if not url:
        return f'{name} : {text}<br>'
    return f'{name} : <a href="{url}">{text}</a><br>'

credits = """
<br><br><br>
<b>[ CREDIT ]</b>
<br><br><br>
""".replace('\n', '<br>')

patreon = """Special thanks<br><b>[ PATRONS ]</b>
Arthur Bookstein
Haruka
Luis Alberto, Letona Quispe
GP O'Byrne
Tobias Klös
07951350313540
Ernest Chan
Douglas Beeman
Daniel Kohl-Fink
Gabriel Vinicio Guedes
Tim
Haley Schwarz
Kurt Grabow
Ketan Pal
Kyle Mondlak
Lily
NamelessGO
Oleksandr Pashchenko
Alba Grecia Suárez Recuay
Alex D
Jesse Asiedu
ElAnki
oiuhroiehg
Tae Lee
Ashok Rajpurohit
Renoaldo Costa Silva Junior
Felipe Dias
Fahim Shaik
Corentin
Yitzhak Bar Geva
龍星 武田
Muneeb Khan
Hikori
Lê Hoàng Phúc
Tobias Günther
NoirHassassin
Jk
Jake Stucki
Cole Krueger
K
Aaron Buckley
KM
Ansel Ng
Victor Evangelista
Moritz Bluhm
Maik C.
Ricardo Escobar
Daniel Valcárcel Málaga
Lerner Alcala
Jason Liu
Blake
Rogelio Rojas
Bunion Bandit
ifjymk
Melchior Schilling
Адріан Недбайло
철수 박
Lisette Lerma
Abhi S
Robert Malone
On The Path Of Righteousness
Wei
Tyler Schulte
Jonathan Contreras
Osasere Osula
Morgan Torres
Natalia Ostaszewska
Jordyn Kindness
Wa sup
Patrick Lee
Jacob Royce
Mattia Adami
Gregory Dance
Adrine
Carlos Garcia
Matthew Hartford
cedox
Jonny MacEachern
🌠
Tan Mun Ling
Martin Gerlach
Knightwalker
Lukas Hammerschmidt
HORUS ™
as cam
Richard Fernandez
K Chuong Dang
Hashem Hanaktah
Justin Skariah
Marli
Ella Schultz
Ali Abid
Siva Garapati
Nitin Chetla
hubert tuyishime
J
Dan S
Salman Majid
C
Maduka Gunasinghe
Marcin Skic
Andreas China
anonymous
Chanho Youne
Dhenis Ferisco
Wave
Foxy_null
WolfsForever
César Flores
Abufit Club
JB Eyring
Yazan Bouchi
Corey
mootcourt
Peter McCabe
Daniel Chien
D N
Mrudang
Yon Uni
Saad
Jared
Mohull Mehta
Xeno G
Theodore Addo
Robert Balisong
Greg
Philly
Đen Trắng
Rae Hanna
Natalie
Michael Pekala
Fraol Feye
Cameron M
Omar Toro
Keeler Kime
Melvin Ezennia
Nailah Kahotep
Sean Voiers
Isabel Guan
Ken
Thương Lê
Sneed100
Nadia Esparza
Stellate ggl
Leo K Nguyen
Vanessa Le
R B
Aurora Dzurko
Aayush Bhatawadekar
Oroygutan
Luke VIP
Abhishek Sharma


""".replace('\n', '<br>')

sound =("<b>[ SOUNDS & BGM ]</b><br>"+
clink("Sound Effect", "Koukaon lab","https://soundeffect-lab.info/",)+
clink("Music" , "MaouDamashii","https://maou.audio/",)+
clink("Catgirl Voice","Cici Fyre","https://cicifyre.itch.io/")+
clink("Robot Voice","Charlie Pennell Productions©","https://www.charliepennellproductions.com/")+
clink("classical music"," Bernd Krueger","http://www.piano-midi.de/")
)


caractor = ("<b>[ IMAGE&3D MATERIALS ]</b><br>" +
clink("Knight","rvros","https://rvros.itch.io/") +
clink("Hooded","Penzilla","https://penzilla.itch.io/")+
clink("CatGirl","(Unity-chan)Kanbayashi Yuko<br>© Unity Technologies Japan/UCL","https://unity-chan.com/contents/guideline/")+
clink("Monsters","RPG dot(R-do) monta!","http://rpgdot3319.g1.xrea.com/")+
clink("Sushi","Ichika","https://www.ac-illust.com/main/profile.php?id=23341701&area=1")+
clink("Textures","PiiiXL","https://piiixl.itch.io/")+
clink("Banner Materials,Lock on cursor<br>","Nanamiyuki's Atelier","https://nanamiyuki.com/")+
clink("Sniper animated","DJMaesen","https://sketchfab.com/3d-models/sniper-animated-eae1ba5b43ae4bc89b0647fb5d8a2d27")+
clink("Parasite Zombie","Mixamo","https://www.mixamo.com/")+
clink("MiniZombie&RedHat","Fkgcluster","https://fkgcluster.itch.io/survivaltowerdefense")+
clink("BloodEffect","XYEzawr","https://xyezawr.itch.io/gif-free-pixel-effects-pack-5-blood-effects")+
clink("Cats","girlypixels","https://girlypixels.itch.io/")+
clink("Terminator-Core","Fred Drabble","https://sketchfab.com/3d-models/fusion-core-f717683d5502496d9e1ef1f1e1d1cb45" )+
clink("Terminator-Robo","Threedee","https://www.threedee.design/cartoon-robot")+
clink("Meowknight","9E0", "https://9e0.itch.io/")+
clink("Vegetable","Butter Milk","https://butterymilk.itch.io/")+
clink("Flower","kathychow","https://kathychow.itch.io/")

            )


addons = """<b>[ INSPIRED BY ADD-ONS ]</b>
Fanfare
Anki Habitica for 2.1
Life Drain
Progress Bar
Progress Bar original
Progress Bar, cards...
Speed Focus Mode
Hitmarkers
HUMBLE PIE

""".replace('\n', '<br>')

budle = ("<b>[ BUNDLE SOURCE CODE ]</b><br>"+
clink ("BGM","Pyglet","https://pyglet.readthedocs.io/en/latest/index.html")+
clink ("webp","dwebp","https://developers.google.com/speed/webp/download")+
clink ("midi","FluidSynth","https://www.fluidsynth.org/")

)


thankYou = ("""
<br><br><br>
<h3>%s</h3><br>""" % ADDON_TITLE +
clink("Created by", "Shigeyuki","https://www.patreon.com/Shigeyuki")+
"""
<br>
Thank you very much!
<br><br><br><br>
""")