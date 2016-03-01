from __future__ import division #Division retourne floating point number
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from Tkinter import Tk
from tkFileDialog import askopenfilename
#==============================================================================
# 1er mars 2016
# Ce script permet de tracer rapidement les acquisitions experimentales
#==============================================================================

#==============================================================================
# Caracteristiques des instruments
#==============================================================================
def Spectro_Anritsu():
    To_skip = 25
    Delimit = ','
    Couleur = 'r'
    Nom = 'Spectre Optique'
    x = 'Longueur d onde (nm)'
    y = 'Intensite (dBm)'
    Id = 'Spectro_Anritsu'
    return To_skip, Delimit, Couleur, Nom, x, y, Id
    
def Spectro_2_4():
    To_skip = 30
    Delimit = ','
    Couleur = 'r'
    Nom = 'Spectre Optique'
    x = 'Longueur d onde (nm)'
    y = 'Intensite (lin scale)'
    Id = 'Spectro_2_4'
    return To_skip, Delimit, Couleur, Nom, x, y, Id
    
def Oscillo_LeCroy():
    To_skip = 6
    Delimit = ','
    Couleur = 'k'
    Nom = 'Trace temporelle'
    x = 'Temps (s)'
    y = 'Intensite (u.a.)'
    Id = 'Oscillo_LeCroy'
    return To_skip, Delimit, Couleur, Nom, x, y, Id
    
def RF_RohdeSchwarz():
    To_skip = 30
    Delimit = ';'
    Couleur = 'g'
    Nom = 'Spectre Radiofrequence'
    x = 'Frequence (Hz)'
    y = 'Intensite (dBm)'
    Id = 'RF_RohdeSchwarz'
    return To_skip, Delimit, Couleur, Nom, x, y, Id
    
def Oscillo_autoco():
    To_skip = 4
    Delimit = ';'
    Couleur = 'b'
    Nom = 'Trace d autocorrelation'
    x = 'Temps de retard (ps)'
    y = 'Intensite (u.a.)'
    Id = 'Oscillo_autoco'
    return To_skip, Delimit, Couleur, Nom, x, y, Id


def OuvrirFenetreChoix():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    return filename

def Plot(x,y,couleur,titre,xlabel,ylabel):
    sns.set_context("talk")
    plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    plt.plot(x,y, label='',marker='',color=couleur)
    plt.title(titre)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()
    
def DeviceDetect(filename):
    with open(filename, 'r') as f:
        first_line = f.readline()
    if 'LECROY' in first_line: 
        print 'Oscilloscope LeCroy reconnu'
        Appareil = Oscillo_LeCroy()
    elif 'File,' in first_line: 
        print 'Spectro Anritsu reconnu'
        Appareil = Spectro_Anritsu()
    elif 'CSV' in first_line: 
        print 'Spectro 2.4 reconnu'
        Appareil = Spectro_2_4()
    elif 'Type;' in first_line: 
        print 'RF_RohdeSchwarz reconnu'
        Appareil = RF_RohdeSchwarz()
    elif '1000' in first_line: 
        print 'Autoco reconnu'
        Appareil = Oscillo_autoco()
    else:
        print 'Aucun appareil reconnu, autoco choisi'
        Appareil = Oscillo_autoco()
    return Appareil

    
def RecupData(filename,Appareil):
    if Appareil[6] == 'Oscillo_autoco':
        recup = np.loadtxt(filename, skiprows=0)
        NbPts = recup[0]
        datay = recup[4:]/(max(recup[4:]))
        x=[]
        for i in range(0,datay.size):
           x.append((float(i)*10*29.5/NbPts)/1.41) 
        x = np.asarray(x)

        #Recherche max et met a zero
        abscisse_max = datay.argmax()
        x_norm = x - x[abscisse_max]     
        
        data=np.array([x_norm,datay]).T
#        Voir pour remplacer datatype par colonnes pour noms
        return data
    else:
        recup = np.genfromtxt(filename, delimiter=Appareil[1], skip_header=Appareil[0], skip_footer=0)     
        return recup

#==============================================================================
# Programme :
#==============================================================================
#   Ouvre la fenetre de choix du fichier a traiter
filename = OuvrirFenetreChoix()

#Lit la premiere ligne du fichier pour en determiner la provenance
Appareil = DeviceDetect(filename)

#   Recupere les donnees en fonction de l appariel
data = RecupData(filename,Appareil)

#   Trace
Plot(data[:,0],data[:,1], Appareil[2], Appareil[3], Appareil[4], Appareil[5])
