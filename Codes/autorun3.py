from tkinter import * #importe la librairie tktinter
import os
import threading
from PIL import ImageTk, Image
import time

# try:
#     cmd = 'test'
#     if (os.system(cmd) != 0):
#         raise Exception
# except:
#     print("ne marche pas")
os.system('gphoto2 --auto-detect')

#fonction pour lancer le programme conçu pour Nikon
def Nikon():
    os.system('pkill gphoto2') #s'assurer que gphoto2 est disponible et prêt à l'emploi
    time.sleep(0.2)
    os.system('gphoto2 --get-config f-number > ./fnumber.txt ') #récupère la liste des ouvertures qui sera stockée dans un fichier texte
    os.system('gphoto2 --get-config shutterspeed > ./shutterspeed.txt ') #récupère la liste des vitesses d'obturation qui sera stockée dans un fichier texte
    window1.destroy() #ferme la fenêtre
    os.system('python3 Nikon_23_05.py') #exécute le programme Nikon

#fonction pour lancer le programme conçu pour Sony
def Sony():
    os.system('pkill gphoto2')
    window1.destroy() #ferme la fenêtre
    os.system('python3 Sony_7.py') #exécute le programme Sony
 
#fonction pour lancer le programme conçu pour Canon 
def Canon():
    os.system('pkill gphoto2')
    os.system('gphoto2 --get-config aperture > ./fnumber.txt ') #récupère la liste des ouvertures qui sera stockée dans un fichier texte
    os.system('gphoto2 --get-config shutterspeed > ./shutterspeed.txt ') #récupère la liste des vitesses d'obturation qui sera stockée dans un fichier texte
    window1.destroy() #ferme la fenêtre
    os.system('python3 Canon_23_05.py') #exécute le programme Canon
 
#création de l'interface avec Tkinter 
window1 = Tk()
window1.title("Remote DSLR Autorun")
window1.geometry("700x550")
window1.config(background='#119CBF')

label1 = Label(window1, text="Remote DSLR", bg='#119CBF', fg='#FFFFFF')
label1.config(font=("Lato", 44))
label1.pack()

image = PhotoImage(file = r"./Images/dslr.png") 
photoimage = image.subsample(5, 5)
#photoimage=image.resize((50,100),Image.ANTIALIAS)
photo_prec = Label(window1, image=photoimage, bg='#119CBF')
photo_prec.pack()

label2 = Label(window1, text="Bienvenue sur Remote DSLR", bg='#119CBF', fg='#FFFFFF')
label2.pack()

label3 = Label(window1, text="Branchez et allumez votre appareil", bg='#119CBF', fg='#FFFFFF')
label3.pack()

nkn = Button(window1, text="Nikon", bg='grey', fg='white', width=60, command=Nikon)
nkn.pack(pady=10)

sn = Button(window1, text="Sony", bg='grey', fg='white', width=60, command=Sony)
sn.pack(pady=10)

cnn = Button(window1, text="Canon", bg='grey', fg='white', width=60, command=Canon)
cnn.pack(pady=10)

window1.mainloop()
