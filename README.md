# Stop-motion
A software designed in Python to create our own stop-motion videos, it can also command an Arduino with the Orion shield. You can use the actual Orion card as well.
You'll need these dependencies to get started:

///////////////////////////////////////////////////////////////////////////////////////////////////////////////
Veuillez entrer les lignes de commandes suivantes dans le terminal afin d'installer les bibliothèques 
et différents utilitaires permettant de faire fonctionner de manière optimale le code du projet Remote DSLR : 
///////////////////////////////////////////////////////////////////////////////////////////////////////////////

Installation de l’utilitaire python :
sudo apt-get install python-setuptools

Installation de l’utilitaire pip :
sudo apt-get install python3-pip

Si pip ne fonctionne pas, essayer pip3 ( Pour python version 3.x )

Installation de pynput (lecture du clavier) :
pip(3) install pynput

Liaison serielle pour commander l’arduino :
pip(3) install pyserial

Installation de pillow (traitement d'images) :
pip(3) install pillow

Installation d’ImageTk pour PIL:
sudo apt-get install python-pil.imagetk (python 2)
sudo apt-get install python3-pil python3-pil.imagetk (python 3.x)

Installation de OpenCV (traitement d'images en temps réel) :
pip(3) install opencv-python

///////////////////////////////////////////////////////////////////////////////////////////////////////////////
