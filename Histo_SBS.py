from __future__ import division #Division retourne floating point number
import numpy as np
import sys
sys.path.insert(0, "/home/ph/Bureau/These/Rogue Events by SBS/Traitement_Donnees/Scripts_Python")
import matplotlib.pyplot as plt
import csv
from Tkinter import Tk
from tkFileDialog import askopenfilename
#A CHANGER : NOM FICHIER ET TITRE DANS PLOTDEUXHISTOS


def OuvrirFenetreChoix():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    return filename
    
    
def Calcul_SWH(y,x):
    NbPics=reduce(np.add, y)
    PicLimite=round((2/3)*NbPics)   
    i=0
    Pic=0
    while Pic<PicLimite:
        Pic+=y[i]
        i+=1
    IntervalleSup=Pic-PicLimite
    SWH=((IntervalleSup*x[i-1])+np.inner(x[i:-1],y[i:-1]))/(IntervalleSup+sum(y[i:-1]))   
    return(SWH,NbPics)

def Ordre(x,colonne,NomFichierALire):
    def getKey(item):
         return item[colonne]
    En_liste=(sorted(x, key=getKey))
    with open('%s.csv' % NomFichierALire, 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(En_liste)
    return()
    
    
def Plot(x,y,SWH):
    colors1=[]
    colors2=[]
    for item in x:
        if item<2*SWH[0]:
            colors1.append('g')
            colors2.append('r')
        else:
            colors1.append('b')
            colors2.append('b')
    
    plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    plt.figure(1)
    plt.figure(1).suptitle('Resultats numeriques - $\Delta t=200ms$ - $r=14$',fontsize=16,color='b')
    ax=plt.subplot(211)
    plt.bar(x,y,width=0.01,color=colors1,edgecolor=colors1)
    plt.title('Histogramme echelle lineaire',color='green')
    plt.axvline(x=2*SWH[0],color='k')
    plt.figure(1).add_subplot(211).annotate('$2.SWH$',xy=(2*SWH[0],0.8*max(y)),xytext=(2*SWH[0]+(0.1*max(x)),0.75*max(y)),arrowprops=dict(facecolor='black',shrink=0.05),)
    ax.text(0.95, 0.5, 'SWH : %f \n Nombre d evenements : %d \n Peak height/distance : (0.02,5)' %(SWH[0],SWH[1]), style='italic',transform=ax.transAxes, ha='right',verticalalignment='top',
        bbox={'facecolor':'wheat', 'alpha':0.5, 'pad':10})    
    plt.subplot(212)
    plt.bar(x,np.log10(y+1),width=0.005,color=colors2,edgecolor=colors2)
    plt.title('Histogramme echelle log',color='red')
    plt.axvline(x=2*SWH[0],color='k')
    



    plt.show()

    
NomFichierALire = OuvrirFenetreChoix()


#NomFichierALire='../Simu_SBS/021115/HistoSBS_Simu_r20.txt'
#Pour Histos    y : Nb evenements - x : Intensite sans header
data = np.genfromtxt(NomFichierALire, delimiter=',', skip_header=0, skip_footer=0, names=['y', 'x'])

#MISE HISTOGRAMME DANS ORDRE et lecture 
Ordre(data,1,NomFichierALire)
data = np.genfromtxt('%s.csv' % NomFichierALire, delimiter=',', skip_header=0, skip_footer=0, names=['y', 'x'])


#CALCUL SWH A PARTIR DE L HISTO
SWH = Calcul_SWH(data['y'],data['x'])

#PLOT
Plot=Plot(data['x'],data['y'],SWH)
