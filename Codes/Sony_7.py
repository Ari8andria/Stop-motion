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


############################DIVERS WIDGETS###################################################

#Liste des diverses balances des blancs
WBList=['Automatique', 'Jour', 'Ombre', 'Nuageux', 'Incandescent', 'Fluo : Blanc chaud', 'Fluo : Blanc froid', 'Fluo : Blanc neutre', 'Fluo : Jour','Flash', 'Custom', 'Preset1', 'Preset2', 'Preset3']
#Liste des ISO
ISOlist=[100,200,400,800,1600,3200,6400,12800,16000,20000,25600]
#Liste des ouvertures standardes
APTlist=[1.8,2,2.8,3.2,3.5,4,4.5,5,5.6,6.3,7.1,8.0,9.0,10,11,13,14,16,18,20,22]
#Liste des vitesses d'obturation standardes
SPDlist=['10','8','6','5','4','3.2','2.5','2','1.6','1.3','1','0.8','0.6','0.5','0.4','1/3','1/4','1/5','1/6','1/8','1/10','1/13','1/15','1/20','1/25','1/30','1/40','1/50','1/60','1/80','1/100','1/125','1/160','1/200','1/250','1/320','1/400','1/500','1/640','1/800','1/1000','1/1250','1/1600','1/2000','1/2500','1/3200','1/4000','1/5000'] 
#Liste des débits d'images
frameratelist=[10,15,20,25]

############################COMMUNICATION AVEC L'ARDUINO#####################################

#On teste la liaison série pour voir si la carte ORION est détectée
try:
    ser = serial.Serial('/dev/ttyUSB0',9600)
    ser.timeout=1

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
           for i in range (0,10):
               ser.write(b'7')
           for y in range (0,10):
               ser.write(b'8')         
        if key == Key.shift_r: # si la touche shift de droite est relâché
           print("trans stop")
           for i in range (0,10):
               ser.write(b'7')
           for y in range (0,10):
               ser.write(b'8')
               
    def ecoute_clavier():
        with Listener(on_press=on_press,on_release=on_release) as listener:  # Setup the listener
            listener.join()

#Cas si le clavier n'est pas détecté
except:
    print("Micro-contrôleur slider non détecté")

#######################################################VARIABLES GLOBALES########################################

global active #Etat Liveview
active = True
global frame #Nombre de photos
global path #Chemin de l'arborescence des fichiers à enregistrer
global ips #Débit d'image par seconde pour le calcul
global framerate_render #Débit d'images par seconde pour le rendu
global image #Dernière photo prise
global alpha #Niveau de transparence de la dernière photo sur le Liveview
global afvar #Etat de l'autofocus
afvar = False
alpha=0

####################################FONCTIONS A UTILISER##############################################"

#Arrêt du programme
def arreter():
    os.system('pkill gphoto2')
    sys.exit(0)

#Mise au point manuelle
def mapm():
    global active
    global afvar
    afvar = False
    if active :
        subprocess.run(['pkill','-9','gphoto2'])
        time.sleep(0.5)
        os.system('gphoto2 --set-config autofocus=0')
        os.system('gphoto2 --set-config focusmode=0')
        os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
    else:
        os.system('gphoto2 --set-config autofocus=0')
        os.system('gphoto2 --set-config focusmode=0')

#Remise des paramètres à 0 (selon des valeurs standardes)
def reinitialisation():
    global active
    global afvar
    if active:
        if afvar:
            mapm()
            os.system('rm -f '+path+'/capt%03d.JPG' %frame)
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            def actions():
                os.system('gphoto2 --set-config-value iso=100')
                os.system('gphoto2 --set-config-value shutterspeed=1/100')
                os.system('gphoto2 --set-config f-number=0')
                os.system('gphoto2 --set-config whitebalance=0')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
                confirmation.destroy()
                af()
        else:
            os.system('rm -f '+path+'/capt%03d.JPG' %frame)
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            def actions():
                os.system('gphoto2 --set-config-value iso=100')
                os.system('gphoto2 --set-config-value shutterspeed=1/100')
                os.system('gphoto2 --set-config f-number=0')
                os.system('gphoto2 --set-config whitebalance=0')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
                confirmation.destroy()
    else:
        if afvar:
            mapm()
            def actions():
                os.system('gphoto2 --set-config-value iso=100')
                os.system('gphoto2 --set-config-value shutterspeed=1/100')
                os.system('gphoto2 --set-config f-number=0')
                os.system('gphoto2 --set-config whitebalance=0')
                confirmation.destroy()
                af()
        else:
            def actions():
                os.system('gphoto2 --set-config-value iso=100')
                os.system('gphoto2 --set-config-value shutterspeed=1/100')
                os.system('gphoto2 --set-config f-number=0')
                os.system('gphoto2 --set-config whitebalance=0')
                confirmation.destroy()
    confirmation = Tk()
    confirmation.title("Remote DSLR")
    confirmation.geometry("400x150")
    confirmation.config(background='#119CBF')
    question=Label(confirmation, text="Voulez-vous vraiment restaurer les exifs par défauts?\n ISO=100\n Speed=1/100\n Ouverture=la plus grande\n Balance des blancs=Automatique", bg='#119CBF', fg='#FFFFFF')
    question.pack(pady=20)
    oui = Button(confirmation, text="OUI", bg='#838687', fg='#FFFFFF', command=actions)
    oui.pack(side=LEFT, padx=100)
    non = Button(confirmation, text="NON", bg='#838687', fg='#FFFFFF', command=confirmation.destroy)
    non.pack(side=LEFT)

#Active ou désactive le retour d'images en temps réel : le Liveview
def switch():
    global active #active ou not active désigne l'état du liveview
    global afvar
    if active:
        if afvar:
            os.system('pkill gphoto2')
            time.sleep(1)
            mapm()
            active = False
            af()
        else:
            os.system('pkill gphoto2')
            time.sleep(1)
            active = False
    else:
        if afvar:
            mapm()
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            active = True
            show_frame()
            af()
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
    global afvar
    if active :
        if afvar:
            os.system('rm -f '+path+'/capt%03d.JPG' %frame)
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            mapm()
            os.system('gphoto2 --capture-image-and-download --filename '+path+'/capt%03d.JPG' % frame)
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            os.system('cp '+path+'/capt%03d.JPG ' %frame +path+'/prev.JPG')
        else:
            os.system('rm -f '+path+'/capt%03d.JPG' %frame)
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            os.system('gphoto2 --capture-image-and-download --filename '+path+'/capt%03d.JPG' % frame)
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            os.system('cp '+path+'/capt%03d.JPG ' %frame +path+'/prev.JPG')
    else:
        if afvar:
            mapm()
            os.system('rm -f '+path+'/capt%03d.JPG' %frame)
            os.system('gphoto2 --capture-image-and-download --filename '+path+'/capt%03d.JPG' % frame)
            os.system('cp '+path+'/capt%03d.JPG ' %frame +path+'/prev.JPG')
            af()
        else:
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
    global afvar
    frame = frame-1
    picture()

#Détection de l'appareil        
def adetect():
    os.system('gphoto2 --auto-detect')

#Changement de la vitesse d'obturation    
def speedchange(*args):
    global active
    global afvar
    spdval=spd.get()
    if active :
        if afvar:
            mapm()
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            if spdval == '3.2':
                os.system('gphoto2 --set-config-index shutterspeed=10')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '2.5':
                os.system('gphoto2 --set-config-index shutterspeed=11')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '1.6':
                os.system('gphoto2 --set-config-index shutterspeed=13')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '1.3':
                os.system('gphoto2 --set-config-index shutterspeed=14')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '0.8':
                os.system('gphoto2 --set-config-index shutterspeed=16')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '0.6':
                os.system('gphoto2 --set-config-index shutterspeed=17')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '0.5':
                os.system('gphoto2 --set-config-index shutterspeed=18')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '0.4':
                os.system('gphoto2 --set-config-index shutterspeed=19')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            else:
                os.system('gphoto2 --set-config-value shutterspeed='+spdval)
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            af()
        else:
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            if spdval == '3.2':
                os.system('gphoto2 --set-config-index shutterspeed=10')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '2.5':
                os.system('gphoto2 --set-config-index shutterspeed=11')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '1.6':
                os.system('gphoto2 --set-config-index shutterspeed=13')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '1.3':
                os.system('gphoto2 --set-config-index shutterspeed=14')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '0.8':
                os.system('gphoto2 --set-config-index shutterspeed=16')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '0.6':
                os.system('gphoto2 --set-config-index shutterspeed=17')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '0.5':
                os.system('gphoto2 --set-config-index shutterspeed=18')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            elif spdval == '0.4':
                os.system('gphoto2 --set-config-index shutterspeed=19')
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            else:
                os.system('gphoto2 --set-config-value shutterspeed='+spdval)
                os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
    else:
        if afvar:
            mapm()
            if spdval == '3.2':
                os.system('gphoto2 --set-config-index shutterspeed=10')
            elif spdval == '2.5':
                os.system('gphoto2 --set-config-index shutterspeed=11')
            elif spdval == '1.6':
                os.system('gphoto2 --set-config-index shutterspeed=13')
            elif spdval == '1.3':
                os.system('gphoto2 --set-config-index shutterspeed=14')
            elif spdval == '0.8':
                os.system('gphoto2 --set-config-index shutterspeed=16')
            elif spdval == '0.6':
                os.system('gphoto2 --set-config-index shutterspeed=17')
            elif spdval == '0.5':
                os.system('gphoto2 --set-config-index shutterspeed=18')
            elif spdval == '0.4':
                os.system('gphoto2 --set-config-index shutterspeed=19')
            else:
                os.system('gphoto2 --set-config shutterspeed='+spdval)
            af()
        else:
            if spdval == '3.2':
                os.system('gphoto2 --set-config-index shutterspeed=10')
            elif spdval == '2.5':
                os.system('gphoto2 --set-config-index shutterspeed=11')
            elif spdval == '1.6':
                os.system('gphoto2 --set-config-index shutterspeed=13')
            elif spdval == '1.3':
                os.system('gphoto2 --set-config-index shutterspeed=14')
            elif spdval == '0.8':
                os.system('gphoto2 --set-config-index shutterspeed=16')
            elif spdval == '0.6':
                os.system('gphoto2 --set-config-index shutterspeed=17')
            elif spdval == '0.5':
                os.system('gphoto2 --set-config-index shutterspeed=18')
            elif spdval == '0.4':
                os.system('gphoto2 --set-config-index shutterspeed=19')
            else:
                os.system('gphoto2 --set-config shutterspeed='+spdval)

#Changement de l'ouverture    
def aperturechange(*args):
    global active
    global afvar
    aptval=apt.get()
    aptval=aptval.replace('.', ',')
    if active :
        if afvar:
            mapm()
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            os.system('gphoto2 --set-config f-number='+aptval)
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            af()
        else:
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            os.system('gphoto2 --set-config f-number='+aptval)
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
    else:
        if afvar:
            mapm()
            os.system('gphoto2 --set-config f-number='+aptval)
            af()
        else:
            os.system('gphoto2 --set-config f-number='+aptval)

#Activation du mode de mise au point automatique (autofocus)    
def af():
    global active
    global afvar
    afvar = True
    if active :
        subprocess.run(['pkill','-9','gphoto2'])
        time.sleep(0.5)
        os.system('gphoto2 --set-config focusmode=3')
        os.system('gphoto2 --set-config autofocus=1')
        os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
    else:
        os.system('gphoto2 --set-config focusmode=3')
        os.system('gphoto2 --set-config autofocus=1')

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
    global afvar
    if active :
        if afvar:
            mapm()
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            if w.get()=='Automatique':
                os.system('gphoto2 --set-config whitebalance=0')
            elif w.get()=='Jour':
                os.system('gphoto2 --set-config whitebalance=1')
            elif w.get()=='Ombre':
                os.system('gphoto2 --set-config whitebalance=2')
            elif w.get()=='Nuageux':
                os.system('gphoto2 --set-config whitebalance=3')
            elif w.get()=='Incandescent':
                os.system('gphoto2 --set-config whitebalance=4')
            elif w.get()=='Fluo : Blanc chaud':
                os.system('gphoto2 --set-config whitebalance=5')
            elif w.get()=='Fluo : Blanc froid':
                os.system('gphoto2 --set-config whitebalance=6')
            elif w.get()=='Fluo : Blanc neutre':
                os.system('gphoto2 --set-config whitebalance=7')
            elif w.get()=='Fluo : Jour':
                os.system('gphoto2 --set-config whitebalance=8')
            elif w.get()=='Flash':
                os.system('gphoto2 --set-config whitebalance=9')
            elif w.get()=='Custom':
                os.system('gphoto2 --set-config whitebalance=10')
            elif w.get()=='Preset1':
                os.system('gphoto2 --set-config whitebalance=11')
            elif w.get()=='Preset2':
                os.system('gphoto2 --set-config whitebalance=12')
            else:
                os.system('gphoto2 --set-config whitebalance=13')
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            af()
        else:
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            if w.get()=='Automatique':
                os.system('gphoto2 --set-config whitebalance=0')
            elif w.get()=='Jour':
                os.system('gphoto2 --set-config whitebalance=1')
            elif w.get()=='Ombre':
                os.system('gphoto2 --set-config whitebalance=2')
            elif w.get()=='Nuageux':
                os.system('gphoto2 --set-config whitebalance=3')
            elif w.get()=='Incandescent':
                os.system('gphoto2 --set-config whitebalance=4')
            elif w.get()=='Fluo : Blanc chaud':
                os.system('gphoto2 --set-config whitebalance=5')
            elif w.get()=='Fluo : Blanc froid':
                os.system('gphoto2 --set-config whitebalance=6')
            elif w.get()=='Fluo : Blanc neutre':
                os.system('gphoto2 --set-config whitebalance=7')
            elif w.get()=='Fluo : Jour':
                os.system('gphoto2 --set-config whitebalance=8')
            elif w.get()=='Flash':
                os.system('gphoto2 --set-config whitebalance=9')
            elif w.get()=='Custom':
                os.system('gphoto2 --set-config whitebalance=10')
            elif w.get()=='Preset1':
                os.system('gphoto2 --set-config whitebalance=11')
            elif w.get()=='Preset2':
                os.system('gphoto2 --set-config whitebalance=12')
            else:
                os.system('gphoto2 --set-config whitebalance=13')
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
    else:
        if afvar:
            mapm()
            if w.get()=='Automatique':
                os.system('gphoto2 --set-config whitebalance=0')
            elif w.get()=='Jour':
                os.system('gphoto2 --set-config whitebalance=1')
            elif w.get()=='Ombre':
                os.system('gphoto2 --set-config whitebalance=2')
            elif w.get()=='Nuageux':
                os.system('gphoto2 --set-config whitebalance=3')
            elif w.get()=='Incandescent':
                os.system('gphoto2 --set-config whitebalance=4')
            elif w.get()=='Fluo : Blanc chaud':
                os.system('gphoto2 --set-config whitebalance=5')
            elif w.get()=='Fluo : Blanc froid':
                os.system('gphoto2 --set-config whitebalance=6')
            elif w.get()=='Fluo : Blanc neutre':
                os.system('gphoto2 --set-config whitebalance=7')
            elif w.get()=='Fluo : Jour':
                os.system('gphoto2 --set-config whitebalance=8')
            elif w.get()=='Flash':
                os.system('gphoto2 --set-config whitebalance=9')
            elif w.get()=='Custom':
                os.system('gphoto2 --set-config whitebalance=10')
            elif w.get()=='Preset1':
                os.system('gphoto2 --set-config whitebalance=11')
            elif w.get()=='Preset2':
                os.system('gphoto2 --set-config whitebalance=12')
            else:
                os.system('gphoto2 --set-config whitebalance=13')
            af()
        else:
            if w.get()=='Automatique':
                os.system('gphoto2 --set-config whitebalance=0')
            elif w.get()=='Jour':
                os.system('gphoto2 --set-config whitebalance=1')
            elif w.get()=='Ombre':
                os.system('gphoto2 --set-config whitebalance=2')
            elif w.get()=='Nuageux':
                os.system('gphoto2 --set-config whitebalance=3')
            elif w.get()=='Incandescent':
                os.system('gphoto2 --set-config whitebalance=4')
            elif w.get()=='Fluo : Blanc chaud':
                os.system('gphoto2 --set-config whitebalance=5')
            elif w.get()=='Fluo : Blanc froid':
                os.system('gphoto2 --set-config whitebalance=6')
            elif w.get()=='Fluo : Blanc neutre':
                os.system('gphoto2 --set-config whitebalance=7')
            elif w.get()=='Fluo : Jour':
                os.system('gphoto2 --set-config whitebalance=8')
            elif w.get()=='Flash':
                os.system('gphoto2 --set-config whitebalance=9')
            elif w.get()=='Custom':
                os.system('gphoto2 --set-config whitebalance=10')
            elif w.get()=='Preset1':
                os.system('gphoto2 --set-config whitebalance=11')
            elif w.get()=='Preset2':
                os.system('gphoto2 --set-config whitebalance=12')
            else:
                os.system('gphoto2 --set-config whitebalance=13')
            

#Changement de l'ISO
def callback_iso(*args):
    global active
    global afvar
    value = x.get()
    if active:
        if afvar:
            mapm()
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            os.system('gphoto2 --set-config-value iso='+value )
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            af()
        else:
            subprocess.run(['pkill','-9','gphoto2'])
            time.sleep(0.5)
            mapm()
            os.system('gphoto2 --set-config-value iso='+value )
            os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
            
    else:
        if afvar:
            mapm()
            os.system('gphoto2 --set-config-value iso='+value )
            af()
        else:
            os.system('gphoto2 --set-config-value iso='+value )
    
#Affichage de la dernière image
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

#Affiche la dernière photo    
def review():
    global path
    img = Image.open(path+"/prev.JPG")
    load = img. resize((300, 200), Image. ANTIALIAS)
    preview = ImageTk.PhotoImage(load)
    photo_prec = Label(postview, image=preview)
    photo_prec.image = preview
    photo_prec.place(x=0, y=0)

#Lance le programme d'aide    
def aide():
    os.system('python3 aide.py')

#Demande si la photo doit être concervée sur l'APN ou non (ne marche hélas pas chez Sony...)
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
    
    mapm()
    os.system('gphoto2 --set-config-value iso=100')
    os.system('gphoto2 --set-config shutterspeed=1/100')
    os.system('gphoto2 --set-config f-number=0')
    os.system('gphoto2 --set-config-index whitebalance=0')
        
    NoL.mainloop()
        
#################################################BOUCLE PRINCIPALE##############################################

#Initialisation
try:
    threading.Thread(target=ecoute_clavier).start() #ON FAIT UN THREAD CAR ON ECOUTE EN PERMANENCE
except:
    print('impossibe de lancer le slider')
    
os.system('gphoto2 --capture-movie --stdout>fifo.mjpg &')
commencer()

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

#######################################################MISE EN FORME AVEC TKINTER ###############################################

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

#####################Frame du haut##############################################################################

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

Rein= Button(frame1, text="REINIT", bg='#838687', fg='#FFFFFF', command=reinitialisation)
Rein.pack(side=LEFT, padx=40)

#configuration avec menu déroulant
icon = PhotoImage(file = r"Sources/Settings.png") #importer l'icon
photoimage = icon.subsample(13, 13) #redimensioner
menuConfiguration= Menubutton(frame1, image=photoimage, borderwidth=0, bg='#119CBF')
menuConfiguration.pack(side=RIGHT, padx=40)
menuderoulant= Menu(menuConfiguration)
menuderoulant.add_command(label='Force Transversal', command=fortrans)
menuderoulant.add_command(label='Force Panoramique', command=forpan)
menuderoulant.add_command(label='Force Tilt', command=fortilt)
menuConfiguration.configure(menu=menuderoulant)

frame1.pack(pady=20, side=TOP)

#######################Frame de gauche##########################################################################

left_frame = Frame(window, bg='#119CBF')

label_iso = Button(left_frame, text="ISO", bg='#119CBF', fg='#000000')
label_iso.grid(row=0, column=0, sticky=W)
x = StringVar()
x.set(ISOlist[0])
iso_menu = OptionMenu(left_frame, x, *ISOlist)
iso_menu.grid(row=0, column=1, sticky=W)
x.trace("w", callback_iso)

bouton_aperture = Button(left_frame, text="APERTURE", bg='#838687', fg='#FFFFFF', width=10, command=aperturechange)
bouton_aperture.grid(row=1, column=0, sticky=W, pady=40)
apt = StringVar()
apt.set(APTlist[0])
apt_menu = OptionMenu(left_frame, apt, *APTlist)
apt_menu.grid(row=1, column=1, sticky=W)
apt.trace("w", aperturechange)

bouton_speed = Button(left_frame, text="SPEED", bg='#838687', fg='#FFFFFF', command=speedchange)
bouton_speed.grid(row=2, column=0, sticky=W)
spd = StringVar()
spd.set(SPDlist[0])
spd_menu = OptionMenu(left_frame, spd, *SPDlist)
spd_menu.grid(row=2, column=1, columnspan=3, sticky=W)
spd_menu.config(width = 10)
spd.trace("w", speedchange)

wbalance = Button(left_frame, text="BALANCE", bg='#838687', fg='#FFFFFF')
wbalance.grid(row=3, column=0, sticky=W, pady=40)

w = StringVar()
w.set(WBList[0])
wb = OptionMenu(left_frame, w, *WBList)
wb.grid(row=3, column=1, sticky=W)
w.trace("w", callback_wb)


left_frame.pack(padx=20, side=LEFT)

#######################Frame de droite##########################################################################

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

retake = Button(window, text="REFAIRE", bg='#838687', fg='#FFFFFF', command=repicture)
retake.place(x=290,y=345)

############################################LIVEVIEW#############################################

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

label_longueur = Label(info, text="Longueur actuelle de votre film:", bg='#119CBF', fg='black')
label_longueur.config(font=("Lato", 15))
label_longueur.grid(row=1,column=0)
duree_seconde = Label(info, bg='grey', fg='white',width=5)
duree_seconde.grid(row=1, column=1, sticky=W, padx=10)
duree_image = Label(info, bg='grey', fg='white',width=5)
duree_image.grid(row=2, column=1, sticky=W, padx=10, pady=10)

info.place(x=290,y=380)

window.mainloop()

