from tkinter import *
import pickle
from tkinter import filedialog
import os
from tkinter import messagebox

global path
def choix():
    global path
    dico: dict={}
    file = filedialog.askopenfile(mode="rb",defaultextension='*.pickle')
    dico=pickle.load(file)
    file.close()
    path=dico["chemin"]
    print(path)

global fr
fr = "10"
global encod
encod = "libx264"
global encap
encap = ".mp4"

def callback_codec(*args):
    global encod
    if w.get()=="H264/MPEG4P10":
        encod = "libx264"
    if w.get()=="H265/HEVC":
        encod = "libx265"
    if w.get()=="Apple ProRes":
        encod = "prores"
    if w.get()=="DNxHD":
        encod = "dnxhd"
    if w.get()=="FLV":
        encod = "flv"
    if w.get()=="MJpeg":
        encod = "mjpeg"
    print(encod)

def callback_framerate(*args):
    global fr
    fr = x.get()
    print(fr)
    
def callback_encapsuleur(*args):
    global encap
    encap = y.get()
    print(encap)

def rendu():
    global path
    global fr
    global encod
    global encap
    nom = filedialog.asksaveasfilename(defaultextension=encap)
    os.system("ffmpeg -r "+fr+" -f image2 -i "+path+"/capt%03d.JPG -r "+fr+" -codec:v "+encod+" "+nom)
    sys.exit(0)

codecs = ["H264/MPEG4P10","H265/HEVC","Apple ProRes","DNxHD","FLV", "MJpeg"]
encapsuleurs = [".mp4", ".avi", ".mov", ".mxf", ".mjpg"]
framerate = ["10","15","20", "25","30","60"]

window1 = Tk()
window1.title("Remote DSLR Rendu")
window1.geometry("450x320")
window1.config(background='#119CBF')

label1 = Label(window1, text="Rendu", bg='#119CBF', fg='#FFFFFF')
label1.config(font=("Lato", 44))
label1.grid(row=0, column=1, pady=10)

choice = Button(window1, text="choisir la sauvegarde", command=choix)
choice.grid(row=1, column=1)

######codecs
encodage = Label(window1, text="CODEC",bg='#119CBF', fg='#000000')
encodage.config(font=("Lato", 15))
encodage.grid(row=2, column=0, sticky=W, pady=10)

w = StringVar()
w.set(codecs[0])
CODECS = OptionMenu(window1, w, *codecs)
CODECS.grid(row=2, column=2, sticky=W)
w.trace("w", callback_codec)

#####framerate
freq = Label(window1, text="FRAMERATE",bg='#119CBF', fg='#000000')
freq.config(font=("Lato", 15))
freq.grid(row=3, column=0, sticky=W, pady=10)

x = StringVar()
x.set(framerate[0])
FREQ = OptionMenu(window1, x, *framerate)
FREQ.grid(row=3, column=2, sticky=W)
x.trace("w", callback_framerate)

####encapsuleur
caps = Label(window1, text="CONTENEUR",bg='#119CBF', fg='#000000')
caps.config(font=("Lato", 15))
caps.grid(row=4, column=0, sticky=W, pady=10)

y = StringVar()
y.set(encapsuleurs[0])
CAPS = OptionMenu(window1, y, *encapsuleurs)
CAPS.grid(row=4, column=2, sticky=W)
y.trace("w", callback_encapsuleur)

render = Button(window1, text="EXPORTER", command=rendu)
render.grid(row=5, column=1, pady=10)

messagebox.showinfo("reminder", "Assurez-vous de bien sauvegarder le projet pour pouvoir exécuter le rendu")

window1.mainloop()