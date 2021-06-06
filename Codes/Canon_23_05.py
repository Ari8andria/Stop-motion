from tkinter import * #importe la librairie tktinter
from tkinter import filedialog
from tkinter import messagebox
import os
from pynput import keyboard
import threading
from pynput.keyboard import Listener, Key
import serial
from PIL import Image, ImageTk
import cv2
import numpy as np
import time
import pickle
import subprocess

############################COMMUNICATION AVEC L'ARDUINO#####################################

#On teste la liaison série pour voir si la carte ORION est détectée
try:
    ser = serial.Serial('/dev/ttyUSB1',9600)
    ser.timeout=1
#Cas si la connexion n'aboutie pas
except:
    print("Micro-contrôleur slider non détecté")

#programme servant à contrôler le slider via envoie d'information en série sous forme d'un caractère
def on_press(key):     
    if key == Key.up:  # si le bouton directionnel haut est pressé
        print("tilt up")
        ser.write(b'2')
    elif key == Key.down:  # si le bouton directionnel bas est pressé
        print("tilt down")
        ser.write(b'0')
    elif key == Key.left:  # si le bouton directionnel gauche est pressé
        print("pan left")
        ser.write(b'3')
    elif key == Key.right:  # si le bouton directionnel droit est pressé
        print("pan right")
        ser.write(b'4')
    elif key == Key.enter:  # si la touche entreé est pressée
        print("Go forward")
        ser.write(b'5')
    elif key == Key.shift_r:  # si la touche shift de droite est pressé
        print("Go backward")
        ser.write(b'6')
        
def on_release(key):
    if key == Key.up: # si le bouton directionnel haut est relâché
       print("tilt stop")
       for i in range (0,20):
           ser.write(b'1')
    if key == Key.down: # si le bouton directionnel bas est relâché
        print("tilt stop")
        for i in range (0,20):
            ser.write(b'1')
    if key == Key.enter: # si la touche entrée est relâché
       print("trans stop")
       for i in range (0,20):
           ser.write(b'7')
    if key == Key.shift_r: # si la touche shift de droite est relâché
       print("trans stop")
       for i in range (0,20):
           ser.write(b'7')
           
def ecoute_clavier():
    with Listener(on_press=on_press,on_release=on_release) as listener:  # Setup the listener
        listener.join()


    
############################DIVERS WIDGETS###################################################

#lecture du fichier contenant les valeurs d'ouverture possible
f = open("./fnumber.txt", "r", encoding="utf-8")
gphoto2_data: str = f.read()
f.close()

f_number_dict: dict = {}
my_key: str
my_value: str

for line in gphoto2_data.split('\n'):
    if line == "END" or line == "":
        continue
    line_list: list = line.split(':')
    line_list[0] = line_list[0].strip()
    line_list[1] = line_list[1].strip()
    if line_list[0] == "Choice":
        if 'Choice' not in f_number_dict:
            f_number_dict.update({'Choice': {}})
        my_key, my_value = line_list[1].split(' ')
        f_number_dict['Choice'].update({my_key: my_value})
    else:
        f_number_dict.update({line_list[0]: line_list[1]})

array = len(f_number_dict['Choice'])*[0]
for i in f_number_dict['Choice']:
    array[int(i)] = f_number_dict['Choice'][i]

#listes à utiliser plus tard :

#Liste des diverses balances des blancs
WBList=['Automatique', 'Nuageux', 'Tungstène', 'Flash', 'Custom', 'Fluo', 'Lumière du jour', 'Ombre']  
#Liste des ISO
ISOlist=[100,200,400,800,1600,3200,6400,12800]
#Liste des débits d'images
frameratelist=[10,15,20,25]

#lecture du fichier contenant les valeurs de vitesses possibles
speed = open("./shutterspeed.txt", "r", encoding="utf-8")
speed_data: str = speed.read()
speed.close()

speed_dict: dict = {}
my_key_speed: str
my_value_speed: str

for line in speed_data.split('\n'):
    if line == "END" or line == "":
        continue
    liste_ligne: list = line.split(':')
    liste_ligne[0] = liste_ligne[0].strip()
    liste_ligne[1] = liste_ligne[1].strip()
    if liste_ligne[0] == "Choice":
        if 'Choice' not in speed_dict:
            speed_dict.update({'Choice': {}})
        my_key_speed, my_value_speed = liste_ligne[1].split(' ')
        speed_dict['Choice'].update({my_key_speed: my_value_speed})
    else:
        speed_dict.update({liste_ligne[0]: liste_ligne[1]})

array_speed = len(speed_dict['Choice'])*[0] #créer une liste avec 
for i in speed_dict['Choice']:
    array_speed[int(i)] = speed_dict['Choice'][i]

#######################################################VARIABLES GLOBALES########################################

global active #Etat Liveview
active = True
global frame #Nombre de photos
global path #Chemin de l'arborescence des fichiers à enregistrer
global ips #Débit d'image par seconde pour le calcul
global framerate_render #Débit d'images par seconde pour le rendu
global image #Dernière photo prise
global alpha  #Niveau de transparence de la dernière photo sur le Liveview
alpha=0
global garde #Etat de la conservation sur l'APN des photos
####################################FONCTIONS A UTILISER##############################################"

#Arrêt du programme
def arreter():
    os.system('pkill gphoto2')
    sys.exit(0)

#Mise au point manuelle
def mapm():
    messagebox.showinfo('Default', 'Pas encore disponible')

#Remise des paramètres à 0 (selon des valeurs standardes)
def reinitialisation():
    os.system('pkill -9 gphoto2')
    try:
        if(os.system('gphoto2 --set-config-index iso=0')!=0):
            raise Exception
    except:
        messagebox.showinfo('Indétecté', "Vérifiez que l'appareil est bien branché et relancez le programme")
    os.system('gphoto2 --set-config shutterspeed=1/100')
    os.system('gphoto2 --set-config-index aperture=0')

#Active ou désactive le retour d'images en temps réel : le Liveview
def switch():
    global active #active ou not active désigne l'état du liveview
    if active:
        os.system('pkill gphoto2')
        time.sleep(0.5)
        active = False
    else:
        os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
        active = True
        show_frame()

#Prend une photo          
def picture():
    global active
    global frame
    global path
    global image
    global active
    global garde
    if active :
        if garde :
            os.system('rm -f '+path+'/capt%03d.JPG' %frame)
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            os.system('gphoto2 --set-config capturetarget=1')
            os.system('gphoto2 --capture-image-and-download --filename '+path+'/capt%03d.JPG --keep' % frame)
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            os.system('cp '+path+'/capt%03d.JPG ' %frame +path+'/prev.JPG')
        else:
            os.system('rm -f '+path+'/capt%03d.JPG' %frame)
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            os.system('gphoto2 --set-config capturetarget=0')
            os.system('gphoto2 --capture-image-and-download --filename '+path+'/capt%03d.JPG' % frame)
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            os.system('cp '+path+'/capt%03d.JPG ' %frame +path+'/prev.JPG')
    else:
        if garde :
            os.system('gphoto2 --set-config capturetarget=1')
            os.system('rm -f '+path+'/capt%03d.JPG' %frame)
            os.system('gphoto2 --capture-image-and-download --filename '+path+'/capt%03d.JPG --keep' % frame)
            os.system('cp '+path+'/capt%03d.JPG ' %frame +path+'/prev.JPG')
        else:
            os.system('gphoto2 --set-config capturetarget=0')
            os.system('rm -f '+path+'/capt%03d.JPG' %frame)
            os.system('gphoto2 --capture-image-and-download --filename '+path+'/capt%03d.JPG' % frame)
            os.system('cp '+path+'/capt%03d.JPG ' %frame +path+'/prev.JPG')
    frame += 1
    image = cv2.imread(path+'/prev.JPG')
    review()

#Décompte la photo précédente et reprend une photo (utile en cas d'erreur)        
def repicture():
    global frame
    global active
    frame = frame-1
    picture()

#Détection de l'appareil         
def adetect():
    os.system('gphoto2 --auto-detect')
 
#Fait la mise au point 
def af():
    if active :
        messagebox.showinfo("Liveview actif", "Veuillez désactiver le liveview avant toute autre opération")      
    else:
        os.system('gphoto2 --set-config autofocusdrive=1')
        switch()

#Tue toutes les instances actives de notre programme       
def kill():
    global active
    active = False
    os.system('pkill gphoto2')
    os.system('rm fifo.mjpg')
    os.system('mkfifo fifo.mjpg')

#Changement de la balance des blancs      
def callback_wb(*args):
    global active
    if active :
        subprocess.call(['pkill','-9','gphoto2'])
        time.sleep(0.5)
        if w.get()=='Tungstène':
            os.system('gphoto2 --set-config-value whitebalance="Tungsten"') 
        elif w.get()=='Automatique':
            os.system('gphoto2 --set-config-value whitebalance="Auto"')
        elif w.get()=='Nuageux':
            os.system('gphoto2 --set-config-value whitebalance="Cloudy"')
        elif w.get()=='Lumière du jour':
            os.system('gphoto2 --set-config-value whitebalance="Daylight"')
        elif w.get()=='Flash':
            os.system('gphoto2 --set-config-value whitebalance="Flash"')
        elif w.get()=='Fluo':
            os.system('gphoto2 --set-config-value whitebalance="Fluorescent"')
        elif w.get()=='Flash':
            os.system('gphoto2 --set-config-value whitebalance="Flash"')
        elif w.get()=='Ombre':
            os.system('gphoto2 --set-config-value whitebalance="Shade"')
        elif w.get()=='Custom':
            os.system('gphoto2 --set-config-value whitebalance="Manual"')
        time.sleep(0.5)
        os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
        #messagebox.showinfo("Liveview actif", "Veuillez désactiver le liveview avant toute autre opération")
    else:
        if w.get()=='Tungstène':
            try:
                if(os.system('gphoto2 --set-config-value whitebalance="Tungsten"') != 0):
                    raise Exception
            except:
                messagebox.show("Non valable", "Ne fonctionne pas sur cette appareil")
        elif w.get()=='Automatique':
            os.system('gphoto2 --set-config-value whitebalance="Auto"')
        elif w.get()=='Nuageux':
            os.system('gphoto2 --set-config-value whitebalance="Cloudy"')
        elif w.get()=='Lumière du jour':
            os.system('gphoto2 --set-config-value whitebalance="Daylight"')
        elif w.get()=='Flash':
            os.system('gphoto2 --set-config-value whitebalance="Flash"')
        elif w.get()=='Fluo':
            os.system('gphoto2 --set-config-value whitebalance="Fluorescent"')
        elif w.get()=='Flash':
            os.system('gphoto2 --set-config-value whitebalance="Flash"')
        elif w.get()=='Ombre':
            os.system('gphoto2 --set-config-value whitebalance="Shade"')
        elif w.get()=='Custom':
            os.system('gphoto2 --set-config-value whitebalance="Manual"')

#fonction changement d'iso
def callback_iso(*args):
    global active
    value = x.get()
    if active:
        #messagebox.showinfo("Liveview actif", "Veuillez désactiver le liveview avant toute autre opération")
        subprocess.run(['pkill', '-9','gphoto2'])
        time.sleep(0.5)
        os.system('gphoto2 --set-config iso='+value )
        time.sleep(0.5)
        os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
    else:
        os.system('gphoto2 --set-config iso='+value )

#fonction changement d'ouverture
def callback_a(*args):
    global active
    value = a.get()
    if active:
        #messagebox.showinfo("Liveview actif", "Veuillez désactiver le liveview avant toute autre opération")
        subprocess.run(['pkill', '-9','gphoto2'])
        time.sleep(0.5)
        os.system('gphoto2 --set-config-value aperture='+value )
        time.sleep(0.5)
        os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
    else:
        os.system('gphoto2 --set-config-value aperture='+value )

#fonction changement de vitesse
def callback_s(*args):
    global active
    value=s.get()
    if active:
        #messagebox.showinfo("Liveview actif", "Veuillez désactiver le liveview avant toute autre opération")
        subprocess.run(['pkill', '-9','gphoto2'])
        time.sleep(0.5)
        os.system('gphoto2 --set-config-value shutterspeed='+value )
        time.sleep(0.5)
        os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
    else:
        os.system('gphoto2 --set-config-value shutterspeed='+value )

#fonction affichage du liveview
def show_frame():
    global image
    _, frame = cap.read()
    if np.shape(frame) != ():     
        height, width, depth = frame.shape
        prec_img = cv2.resize(image,(width,height))
        frame=cv2.addWeighted(frame,1-alpha,prec_img,alpha,0)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)   
        img = Image.fromarray(cv2image)
        intermediaire = img.resize((300, 200))
        imgtk = ImageTk.PhotoImage(image=intermediaire)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(10, show_frame)

#Réglage de la transparence de la dernière image sur le Liveview
def change_alpha(*args):
    global alpha
    alpha=Alpha.get()/10
    print(alpha)

#Calcul la longueur du stop-motion en unité de temps     
def length_update(*args):
    global frame
    global ips
    nb=frame-1
    ips=ips_entry.get()
    duree_image.set(nb)
    duree_seconde.set(nb)

#Enregistrement du projet    
def saveas():
    global frame
    global path
    dico: dict = {}
    dico["chemin"]=path
    dico["numero_image"]=frame
    filename = filedialog.asksaveasfilename(defaultextension=".pickle")
    output_file = open(filename, "wb")
    pickle.dump(dico, output_file)
    output_file.close()

#Demande du débit d'images      
def callback_fr(*args):
    global framerate_render
    framerate_render = fr.get()
    print(framerate_render)

#Lance le programme de rendu   
def rendu():
    os.system('python3 rendu.py')

#Lance le programme d'aide    
def aide():
    os.system('python3 aide.py')

#Demande si la photo doit être concervée sur l'APN ou non 
def conservation():
    global garde
    conservationfen = Tk()
    conservationfen.title("Remote DSLR")
    conservationfen.geometry("400x150")
    conservationfen.config(background='#119CBF')
    def gardeoui():
        global garde
        garde = True
        print(garde)
        conservationfen.destroy()
    def gardenon():
        global garde
        garde = False
        print(garde)
        conservationfen.destroy()
    question=Label(conservationfen, text="Voulez-vous conserver les photos sur votre appareil ?", bg='#119CBF', fg='#FFFFFF')
    question.pack(pady=20)
    oui = Button(conservationfen, text="OUI", bg='#838687', fg='#FFFFFF', command=gardeoui)
    oui.pack(side=LEFT, padx=100)
    non = Button(conservationfen, text="NON", bg='#838687', fg='#FFFFFF', command=gardenon)
    non.pack(side=LEFT)

#Définie la vitesse de déplacement sur l'axe transversal    
def fortrans():
    def quart():
        ser.write(b'a')
        fortransfen.destroy()
    def demie():
        ser.write(b'b')
        fortransfen.destroy()
    def tquart():
        ser.write(b'c')
        fortransfen.destroy()
    def entier():
        ser.write(b'd')
        fortransfen.destroy()
    fortransfen = Tk()
    fortransfen.title("Remote DSLR")
    fortransfen.geometry("400x150")
    fortransfen.config(background='#119CBF')
    question=Label(fortransfen, text="Taux de vitesse sur l'axe transversal ?", bg='#119CBF', fg='#FFFFFF')
    question.place(x=50,y=10)
    quart = Button(fortransfen, text="25%", bg='#838687', fg='#FFFFFF', command=quart)
    quart.grid(row=5, column=1, pady=50, padx=20)
    demie = Button(fortransfen, text="50%", bg='#838687', fg='#FFFFFF', command=demie)
    demie.grid(row=5, column=2, padx=20)
    tquart = Button(fortransfen, text="75%", bg='#838687', fg='#FFFFFF', command=tquart)
    tquart.grid(row=5, column=3, padx=20)
    entier = Button(fortransfen, text="100%", bg='#838687', fg='#FFFFFF', command=entier)
    entier.grid(row=5, column=4, padx=20)

#Définie la vitesse de déplacement sur l'axe des panoramiques     
def forpan():
    def quart1():
        ser.write(b'e')
        forpan.destroy()
    def demie1():
        ser.write(b'f')
        forpan.destroy()
    def tquart1():
        ser.write(b'g')
        forpan.destroy()
    def entier1():
        ser.write(b'h')
        forpan.destroy()
    forpan = Tk()
    forpan.title("Remote DSLR")
    forpan.geometry("400x150")
    forpan.config(background='#119CBF')
    question=Label(forpan, text="Taux de vitesse sur l'axe panoramique ?", bg='#119CBF', fg='#FFFFFF')
    question.place(x=50,y=10)
    quart = Button(forpan, text="25%", bg='#838687', fg='#FFFFFF', command=quart1)
    quart.grid(row=5, column=1, pady=50, padx=20)
    demie = Button(forpan, text="50%", bg='#838687', fg='#FFFFFF', command=demie1)
    demie.grid(row=5, column=2, padx=20)
    tquart = Button(forpan, text="75%", bg='#838687', fg='#FFFFFF', command=tquart1)
    tquart.grid(row=5, column=3, padx=20)
    entier = Button(forpan, text="100%", bg='#838687', fg='#FFFFFF', command=entier1)
    entier.grid(row=5, column=4, padx=20)

#Définie la vitesse de déplacement sur l'axe des tilts      
def fortilt():
    def quart2():
        ser.write(b'i')
        fortilt.destroy()
    def demie2():
        ser.write(b'j')
        fortilt.destroy()
    def tquart2():
        ser.write(b'k')
        fortilt.destroy()
    def entier2():
        ser.write(b'l')
        fortilt.destroy()
    fortilt = Tk()
    fortilt.title("Remote DSLR")
    fortilt.geometry("400x150")
    fortilt.config(background='#119CBF')
    question=Label(fortilt, text="Taux de vitesse sur l'axe du tilt ?", bg='#119CBF', fg='#FFFFFF')
    question.place(x=50,y=10)
    quart = Button(fortilt, text="25%", bg='#838687', fg='#FFFFFF', command=quart2)
    quart.grid(row=5, column=1, pady=50, padx=20)
    demie = Button(fortilt, text="50%", bg='#838687', fg='#FFFFFF', command=demie2)
    demie.grid(row=5, column=2, padx=20)
    tquart = Button(fortilt, text="75%", bg='#838687', fg='#FFFFFF', command=tquart2)
    tquart.grid(row=5, column=3, padx=20)
    entier = Button(fortilt, text="100%", bg='#838687', fg='#FFFFFF', command=entier2)
    entier.grid(row=5, column=4, padx=20)
#################################################New/Load########################################################    

#Tout premier lancement du programme
def commencer():
    
    def new():
        global image
        image = cv2.imread('./Images/prev_depart.png')
        global path
        global frame
        frame = 1
        path = filedialog.askdirectory()
        NoL.destroy()
        
    def load_project():
        global image
        global frame
        global path
        dico: dict={}
        file = filedialog.askopenfile(mode="rb",defaultextension='*.pickle')
        dico=pickle.load(file)
        file.close()
        path=dico["chemin"]
        frame=dico["numero_image"]
        print(dico)
        image = cv2.imread(path+'/prev.JPG')
        NoL.destroy()
        
    NoL = Tk()
    NoL.title("Remote DSLR New/Load")
    NoL.config(background='#119CBF')
    NEW = Button(NoL, text="Créer un projet", bg='grey', fg='black', command=new)
    NEW.grid(row = 0, column = 0, sticky=W)
    LOAD = Button(NoL, text="Charger un projet", bg='grey', fg='black', command=load_project)
    LOAD.grid(row = 0, column = 1, sticky=W)
    reinitialisation()
    NoL.mainloop()
#################################################BOUCLE PRINCIPALE##############################################

#initialisation
try:
    threading.Thread(target=ecoute_clavier).start() #ON FAIT UN THREAD CAR ON ECOUTE EN PERMANENCE
except:
    print(1)
commencer()
os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
#image = cv2.imread(path+'/prev.JPG')

#fenetre principale
window = Tk()
window.title("Remote DSLR")
window.geometry("1280x720")
window.minsize(1280,720)
window.maxsize(1280,720)
window.config(background='#119CBF')

############################################Fonction Slider#####################################################

#Différents messages explicatifs selon les boutons appuyés
def tilt_up():
    messagebox.showinfo("tilt","Appuyer sur le bouton 'up'")

def tilt_down():
    messagebox.showinfo("tilt","Appuyer sur le bouton 'down'")
    
def pan_left():
    messagebox.showinfo("pan","Appuyer sur le bouton 'left'")

def pan_right():
    messagebox.showinfo("pan","Appuyer sur le bouton 'right'")
    
def trans_for():
    messagebox.showinfo("trans","Appuyer sur le bouton 'enter'")
    
def trans_back():
    messagebox.showinfo("trans","Appuyer sur le bouton 'shift' droit")
    
def stop():
    messagebox.showinfo("stop","Relâcher la touche pressée")
    
#######################################################GESTION DE PROJET#########################################################

barre_menu = Frame(window, bg='grey')

save = Button(barre_menu, text="Enregistrer le projet", bg='grey', fg='black', command=saveas)
save.pack(side = LEFT)

render = Button(barre_menu, text="Faire un rendu", bg='grey', fg='black', command=rendu)
render.pack(side = LEFT)

HELP = Button(barre_menu, text="Aide", bg='grey', fg='black', command=aide)
HELP.pack(side = LEFT)

STOP = Button(barre_menu, text = "QUITTER", bg='red', fg='white', command=arreter)
STOP.pack(side = RIGHT)

barre_menu.pack(side=TOP, fill=X)

#####################frame du haut
frame1=Frame(window, bg='#119CBF')

detect = Button(frame1, text="DETECT", bg='#838687', fg='#FFFFFF', command=adetect)
detect.pack(side=LEFT)

liveview = Button(frame1, text="LIVEVIEW", bg='#838687', fg='#FFFFFF', command=switch)
liveview.pack(side=LEFT, padx=40)

pic = Button(frame1, text="PHOTO", bg='#838687', fg='#FFFFFF', command=picture)
pic.pack(side=LEFT, padx=0)

AF = Button(frame1, text="AUTOFOCUS", bg='#838687', fg='#FFFFFF', command=af)
AF.pack(side=LEFT, padx=40)

MF = Button(frame1, text="MANUAL", bg='#838687', fg='#FFFFFF', command=mapm)
MF.pack(side=LEFT, padx=0)

#configuration avec menu déroulant
icon = PhotoImage(file = r"Sources/Settings.png") #importer l'icon
photoimage = icon.subsample(13, 13) #redimensioner
menuConfiguration= Menubutton(frame1, image=photoimage, borderwidth=0, bg='#119CBF')
menuConfiguration.pack(side=RIGHT, padx=40)
menuderoulant= Menu(menuConfiguration)
menuderoulant.add_command(label='Conservation photo appareil', command=conservation)
menuderoulant.add_command(label='Force Transversal', command=fortrans)
menuderoulant.add_command(label='Force Panoramique', command=forpan)
menuderoulant.add_command(label='Force Tilt', command=fortilt)
menuConfiguration.configure(menu=menuderoulant)

frame1.pack(pady=20, side=TOP)

#######################frame de gauche
left_frame = Frame(window, bg='#119CBF')


label_iso = Label(left_frame, text="ISO", bg='#119CBF', fg='#000000')
label_iso.config(font=("Lato", 15))
label_iso.grid(row=0, column=0, sticky=W)
x = StringVar()
x.set(ISOlist[0])
iso_menu = OptionMenu(left_frame, x, *ISOlist)
iso_menu.grid(row=0, column=1, sticky=W)
x.trace("w", callback_iso)

label_aperture = Label(left_frame, text="APERTURE", bg='#119CBF', fg='#000000')
label_aperture.grid(row=1, column=0, sticky=W, pady=40)
a = StringVar()
a.set(array[0])
aperture_menu = OptionMenu(left_frame, a, *array)
aperture_menu.grid(row=1, column=1, sticky=W, padx=10)
a.trace("w", callback_a)

label_speed = Label(left_frame, text="SPEED", bg='#119CBF', fg='#000000')
label_speed.grid(row=2, column=0, sticky=W)
s = StringVar()
s.set(array_speed[0])
speed_menu = OptionMenu(left_frame, s, *array_speed)
speed_menu.grid(row=2, column=1, sticky=W, padx=10)
s.trace("w", callback_s)

wbalance = Label(left_frame, text="BALANCE",bg='#119CBF', fg='#000000')
wbalance.config(font=("Lato", 15))
wbalance.grid(row=3, column=0, sticky=W, pady=40)

w = StringVar()
w.set(WBList[0])
wb = OptionMenu(left_frame, w, *WBList)
wb.grid(row=3, column=1, sticky=W)
w.trace("w", callback_wb)

left_frame.pack(padx=20, side=LEFT)

###########################frame de droite
right_frame = Frame(window, bg='#119CBF')

label_tp = Label(right_frame, text = "TILT/PAN")
label_tp.grid(column=3)

ico1 = PhotoImage(file = r"./Images/up.png") #importer l'icon
upico = ico1.subsample(1, 1)
Up = Button(right_frame, image=upico, bg='#838687', fg='#FFFFFF', command=tilt_up)
Up.grid(row=0,column=1,pady=10)

ico2 = PhotoImage(file = r"./Images/left.png") #importer l'icon
leftico = ico2.subsample(1, 1)
Left = Button(right_frame, image=leftico, bg='#838687', fg='#FFFFFF', command=pan_left)
Left.grid(row=1,column=0)

ico3 = PhotoImage(file = r"./Images/stop.png") #importer l'icon
stopico = ico3.subsample(3, 3)
Stop = Button(right_frame, image=stopico, bg='#119CBF', fg='#FFFFFF', command=stop)
Stop.grid(row=1,column=1,padx=10)

ico4 = PhotoImage(file = r"./Images/right.png") #importer l'icon
rightico = ico4.subsample(1, 1)
Right = Button(right_frame, image=rightico, bg='#838687', fg='#FFFFFF', command=pan_right)
Right.grid(row=1,column=2)
    
ico5 = PhotoImage(file = r"./Images/down.png") #importer l'icon
downico = ico5.subsample(1, 1)
Down = Button(right_frame, image=downico, bg='#838687', fg='#FFFFFF', command=tilt_down)
Down.grid(row=2,column=1, pady=10)

label_tr = Label(right_frame, text = "TRANSLATION")
label_tr.grid(row=4, column=3, pady=10)

Trans1 = Button(right_frame, image=leftico, bg='#838687', fg='#FFFFFF', command=trans_for)
Trans1.grid(row=5,column=0)

Stop2 = Button(right_frame, image=stopico, bg='#119CBF', fg='#FFFFFF', command=stop)
Stop2.grid(row=5,column=1,padx=10)

Trans2 = Button(right_frame, image=rightico, bg='#838687', fg='#FFFFFF', command=trans_back)
Trans2.grid(row=5,column=2)

Alpha = Scale(window, from_=0, to=10, command=change_alpha)
Alpha.place(x=950, y=175)

right_frame.pack(padx=20, side=RIGHT)

###########################################AFFICHAGE DE LA DERNIÈRE PHOTO######################################################

postview= Canvas(window, bg='white', width = 300, height = 200)

#Fonction pour afficher la dernière photo
def review():
    global path
    img = Image.open(path+"/prev.JPG")
    load = img. resize((300, 200), Image. ANTIALIAS)
    preview = ImageTk.PhotoImage(load)
    photo_prec = Label(postview, image=preview)
    photo_prec.image = preview
    photo_prec.place(x=0, y=0)

postview.place(x=290,y=140)
#postview.place(x=600, y=140)

retake = Button(window, text="REFAIRE", bg='#838687', fg='#FFFFFF', command=repicture)
retake.place(x=290,y=345)

###################################################LIVEVIEW##################################################################

viewfinder = Frame(window, bg='white', width = 300, height = 200)

width, height = 100, 100

cap = cv2.VideoCapture('fifo.mjpg')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
lmain = Label(viewfinder)
lmain.pack()
threading.Thread(target=show_frame).start()

viewfinder.place(x=600,y=140)

##########################################INFORMATIONS GENERALES###############################################################

info = Frame(window, bg='#119CBF')

label_framerate = Label(info, text="Nombre d'images par secondes:", bg='#119CBF', fg='black')
label_framerate.config(font=("Lato", 15))
label_framerate.grid(row=0,column=0,pady=20)
fr = StringVar()
fr.set(frameratelist[0])
fr_menu = OptionMenu(info, fr, *frameratelist)
fr_menu.grid(row=0, column=1, sticky=W)
fr.trace("w", callback_fr)

label_longueur = Label(info, text="Longueur actuelle de vore film:", bg='#119CBF', fg='black')
label_longueur.config(font=("Lato", 15))
label_longueur.grid(row=1,column=0)
duree_seconde = Label(info, bg='grey', fg='white',width=5)
duree_seconde.grid(row=1, column=1, sticky=W, padx=10)
duree_image = Label(info, bg='grey', fg='white',width=5)
duree_image.grid(row=2, column=1, sticky=W, padx=10, pady=10)

info.place(x=290,y=380)

######################################terminal pour vérifier les erreurs###############################################
terminal_frame = Frame(window, height=100, width=1280)
terminal_frame.place(x=0, y=620)
wid =terminal_frame.winfo_id()
os.system('xterm -into %d -geometry 1280x20 -sb &' % wid)

window.mainloop()



