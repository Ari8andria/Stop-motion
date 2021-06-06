from tkinter import * #importe la librairie tktinter
from tkinter import messagebox

WBList=['Automatique', 'Jour', 'Ombre', 'Nuageux', 'Incandescent', 'Fluo : Blanc chaud', 'Fluo : Blanc froid', 'Fluo : Blanc neutre', 'Fluo : Jour','Flash', 'Custom', 'Preset1', 'Preset2', 'Preset3']
ISOlist=[100,200,400,800,1600,3200,6400,12800,16000,20000,25600]
APTlist=[1.8,2,2.8,3.2,3.5,4,4.5,5,5.6,6.3,7.1,8.0,9.0,10,11,13,14,16,18,20,22]
SPDlist=['10','8','6','5','4','3,2','2,5','2','1,6','1,3','1','0,8','0,6','0,5','0,4','1/3','1/4','1/5','1/6','1/8','1/10','1/13','1/15','1/20','1/25','1/30','1/40','1/50','1/60','1/80','1/100','1/125','1/160','1/200','1/250','1/320','1/400','1/500','1/640','1/800','1/1000','1/1250','1/1600','1/2000','1/2500','1/3200','1/4000','1/5000'] 
frameratelist=[10,15,20,25]

#####Fonction

def mapmhelp():
    messagebox.showinfo("Aide","Met la mise au point en mode manuel")
    
def reinitialisationhelp():
    messagebox.showinfo("Aide","Réinitialise les paramètres de l'APN à des valeures standards (ISO=100, Vitesse d'obturation=1/100, Ouverture la plus grande, Balance des Blancs automatique")

def switchhelp():
    messagebox.showinfo("Aide","Active ou désactive le LiveView (peut-être utile si une action ne marche pas, peut devoir être pressé 2 fois si aucun effet)")
        
def picturehelp():
    messagebox.showinfo("Aide","Prend une photo")
    
def repicturehelp():
    messagebox.showinfo("Aide","Prend une photo et remplace l'ancienne")
        
def adetecthelp():
    messagebox.showinfo("Aide","Détecte votre APN")
    
def speedchangehelp():
    messagebox.showinfo("Aide","Applique la vitesse d'obturation")
    
def speedchangehelp2(*args):
    messagebox.showinfo("Aide","Sélectionne et applique la vitesse d'obturation (pour bien l'utiliser, rester appuyer sur le clique gauche pour sélectionner ou cliquer sur le tiret du bouton")
    
def aperturechangehelp():
    messagebox.showinfo("Aide","Applique l'ouverture")
    
def aperturechangehelp2(*args):
    messagebox.showinfo("Aide","Sélectionne et applique l'ouverture")
    
def afhelp():
    messagebox.showinfo("Aide","Fait la mise au point automatiquement")
        
def callback_wbhelp():
    messagebox.showinfo("Aide","Applique la balance des blancs")
    
def callback_wbhelp2(*args):
    messagebox.showinfo("Aide","Sélectionne et applique la balance des blancs")
    
def callback_isohelp():
    messagebox.showinfo("Aide","Applique la sensibilité")
    
def callback_isohelp2(*args):
    messagebox.showinfo("Aide","Sélectionne et applique la sensibilité")

def tilt_uphelp():
    messagebox.showinfo("tilt","Fait un tilt vers le haut, pour se faire, appuyer sur le bouton 'up'")

def tilt_downhelp():
    messagebox.showinfo("tilt","Fait un tilt vers le bas, pour se faire, appuyer sur le bouton 'down'")
    
def pan_lefthelp():
    messagebox.showinfo("pan","Fait un panoramique vers la gauche, pour se faire, appuyer sur le bouton 'left'")

def pan_righthelp():
    messagebox.showinfo("pan","Fait un panoramique vers la droite, pour se faire, appuyer sur le bouton 'right'")
    
def trans_forhelp():
    messagebox.showinfo("trans","Fait un déplacement transversale vers la partie sans le moteur, pour se faire, appuyer sur le bouton 'enter'")
    
def trans_backhelp():
    messagebox.showinfo("trans","Fait un déplacement transversale vers la partie avec le moteur, pour se faire, appuyer sur le bouton 'shift' droit")
    
def stophelp():
    messagebox.showinfo("stop","Arrête toute action, pour se faire, relâcher la touche pressée")

aide = Tk()
aide.title("Aide")
aide.geometry("1280x720")
aide.minsize(1280,720)
aide.maxsize(1280,720)
aide.config(background='#119CBF')

#####CopieHaut

frame10=Frame(aide, bg='#119CBF')

detect = Button(frame10, text="DETECT", bg='#838687', fg='#FFFFFF', command=adetecthelp)
detect.pack(side=LEFT)

liveview = Button(frame10, text="LIVEVIEW", bg='#838687', fg='#FFFFFF', command=switchhelp)
liveview.pack(side=LEFT, padx=40)

pic = Button(frame10, text="PHOTO", bg='#838687', fg='#FFFFFF', command=picturehelp)
pic.pack(side=LEFT, padx=0)

AF = Button(frame10, text="AUTOFOCUS", bg='#838687', fg='#FFFFFF', command=afhelp)
AF.pack(side=LEFT, padx=40)

MF = Button(frame10, text="MANUAL", bg='#838687', fg='#FFFFFF', command=mapmhelp)
MF.pack(side=LEFT, padx=0)

Rein= Button(frame10, text="REINIT", bg='#838687', fg='#FFFFFF', command=reinitialisationhelp)
Rein.pack(side=LEFT, padx=40)

frame10.pack(pady=20, side=TOP)

#####CopieGauche

left_frame2 = Frame(aide, bg='#119CBF')

label_iso = Button(left_frame2, text="ISO", bg='#119CBF', fg='#000000', command=callback_isohelp)
label_iso.grid(row=0, column=0, sticky=W)
x = StringVar()
x.set(ISOlist[0])
iso_menu = OptionMenu(left_frame2, x, *ISOlist)
iso_menu.grid(row=0, column=1, sticky=W)
x.trace("w", callback_isohelp2)

bouton_aperture = Button(left_frame2, text="APERTURE", bg='#838687', fg='#FFFFFF', width=10, command=aperturechangehelp)
bouton_aperture.grid(row=1, column=0, sticky=W, pady=40)
apt = StringVar()
apt.set(APTlist[0])
apt_menu = OptionMenu(left_frame2, apt, *APTlist)
apt_menu.grid(row=1, column=1, sticky=W)
apt.trace("w", aperturechangehelp2)

bouton_speed = Button(left_frame2, text="SPEED", bg='#838687', fg='#FFFFFF', command=speedchangehelp)
bouton_speed.grid(row=2, column=0, sticky=W)
spd = StringVar()
spd.set(SPDlist[0])
spd_menu = OptionMenu(left_frame2, spd, *SPDlist)
spd_menu.grid(row=2, column=1, columnspan=3, sticky=W)
spd_menu.config(width = 10)
spd.trace("w", speedchangehelp2)

wbalance = Button(left_frame2, text="BALANCE", bg='#838687', fg='#FFFFFF', command=callback_wbhelp)
wbalance.grid(row=3, column=0, sticky=W, pady=40)
w = StringVar()
w.set(WBList[0])
wb = OptionMenu(left_frame2, w, *WBList)
wb.grid(row=3, column=1, sticky=W)
w.trace("w", callback_wbhelp2)


left_frame2.pack(padx=20, side=LEFT)

#####CopieDroite

right_frame2 = Frame(aide, bg='#119CBF')

label_tp = Label(right_frame2, text = "TILT/PAN")
label_tp.grid(column=3)

ico1 = PhotoImage(file = r"./Images/up.png") #importer l'icon
upico = ico1.subsample(1, 1)
Up = Button(right_frame2, image=upico, bg='#838687', fg='#FFFFFF', command=tilt_uphelp)
Up.grid(row=0,column=1,pady=10)

ico2 = PhotoImage(file = r"./Images/left.png") #importer l'icon
leftico = ico2.subsample(1, 1)
Left = Button(right_frame2, image=leftico, bg='#838687', fg='#FFFFFF', command=pan_lefthelp)
Left.grid(row=1,column=0)

ico3 = PhotoImage(file = r"./Images/stop.png") #importer l'icon
stopico = ico3.subsample(3, 3)
Stop = Button(right_frame2, image=stopico, bg='#119CBF', fg='#FFFFFF', command=stophelp)
Stop.grid(row=1,column=1,padx=10)

ico4 = PhotoImage(file = r"./Images/right.png") #importer l'icon
rightico = ico4.subsample(1, 1)
Right = Button(right_frame2, image=rightico, bg='#838687', fg='#FFFFFF', command=pan_righthelp)
Right.grid(row=1,column=2)
    
ico5 = PhotoImage(file = r"./Images/down.png") #importer l'icon
downico = ico5.subsample(1, 1)
Down = Button(right_frame2, image=downico, bg='#838687', fg='#FFFFFF', command=tilt_downhelp)
Down.grid(row=2,column=1, pady=10)

label_tr = Label(right_frame2, text = "TRANSLATION")
label_tr.grid(row=4, column=3, pady=10)

Trans1 = Button(right_frame2, image=leftico, bg='#838687', fg='#FFFFFF', command=trans_forhelp)
Trans1.grid(row=5,column=0)

Stop2 = Button(right_frame2, image=stopico, bg='#119CBF', fg='#FFFFFF', command=stophelp)
Stop2.grid(row=5,column=1,padx=10)

Trans2 = Button(right_frame2, image=rightico, bg='#838687', fg='#FFFFFF', command=trans_backhelp)
Trans2.grid(row=5,column=2)

right_frame2.pack(padx=20, side=RIGHT)

#####Milieu

retake = Button(aide, text="REFAIRE", bg='#838687', fg='#FFFFFF', command=repicturehelp)
retake.place(x=290,y=345)

label_postview = Label(aide, bd=1, width = 37, height = 10, fg='black', text="Dernière photo")
label_postview.place(x=290,y=140)

label_viewfinder = Label(aide, bd=1, width = 37, height = 10, fg='black', text="Retour vidéo")
label_viewfinder.place(x=600,y=140)
 
messagebox.showinfo("Aide","Appuyer sur les boutons pour voir leur fonctionnement")

aide.mainloop()
