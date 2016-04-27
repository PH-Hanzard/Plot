from __future__ import division #Division retourne floating point number
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
from Tkinter import Tk
from tkFileDialog import askopenfilename
#==============================================================================
# 010316 -- PLOT SERIE COURBES SCATTERING -
# A modifier dans Execution 
#    dans Plot_color : Indice initial, Indice final,  Longueur onde centrale, offset
#    dans Res_Fibre : la fibre dispersive utilisee
#==============================================================================

def OuvrirFenetreChoix():
    """
        Ouvre fenetre permettant selection du premier fichier a traiter
        Retourne chemin complet
    """
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    return filename
    
def EditNom(filename,Nb):
    """
        Retire decimales du nom du fichier pour permettre boucle
        ex : EditNom(C1ph00002.txt,9) -> C1ph
        Nb : nombre de chiffres a retirer, extension incluse avec -4
    """
    filename = filename[:-Nb-4]
    return filename
    
def Oscillo_LeCroy():
    """
        Caracteristiques de l oscilloscope LeCroy
    """
    To_skip = 6
    Delimit = ','
#    Delimit = ' '
    DigitsNom = 5
    extention = '.txt'
    return To_skip, Delimit, DigitsNom, extention
    
def Oscillo_Keysight():
    """
        Caracteristiques de l oscilloscope LeCroy
    """
    To_skip = 0
    Delimit = ','
#    Delimit = ' '
    DigitsNom = 5
    extention = '.csv'
    return To_skip, Delimit, DigitsNom, extention
    
def DeviceDetect(filename):
    """
        Lit la premiere ligne du fichier pour detecter sa provenance
    """
    with open(filename, 'r') as f:
        first_line = f.readline()
    if 'LECROY' in first_line: 
        print 'Oscilloscope LeCroy reconnu'
        Appareil = Oscillo_LeCroy()
    else:
        print 'Keysight choisi'
#        Appareil = False
        Appareil = Oscillo_Keysight()
    return Appareil
def normalize(fct):
    """
        Set function's maximum at 1
    """
    return ((fct*1.)/max(fct))

def Fibre_Besancon():
    """
        Caracteristiques fibre DFT. Retourne D * L en ns/nm
    """
    Longueur = 7.7
    D = - 150
    return Longueur * D * 1e-3
    
def Fibre_Lille():
    """
        Caracteristiques fibre DFT. Retourne D * L en ns/nm
    """
    Longueur = 1
    D = - 429
    return Longueur * D * 1e-3
    
def Fibre_Violette():
    """
        Caracteristiques fibre DFT. Retourne D * L en ns/nm
    """
    Longueur = 1.66
    D = - 91
    return Longueur * D * 1e-3
    
def Plot_color(x_i, x_f, Nom, delimit, skiphead, lambda_centre, Scale, offset, LogOrLin, extension):
    """
        Trace l intensite du spectre au fil des tours de cavite
    """
    sns.set_context("talk")
    for i in range(x_i,x_f+1):
#        data = np.genfromtxt(Nom+'%05d.csv'%i, delimiter=delimit, skip_header=skiphead, skip_footer=0, names=['x', 'y'])  
        data = np.genfromtxt((Nom+'%05d'+extension)%i, delimiter=delimit, skip_header=skiphead, skip_footer=0, names=['x', 'y'])  

        y_norm = normalize(data['y'])
        data['x']=((data['x'] * 1e9) / Scale) + lambda_centre + offset
            
        if LogOrLin == 'log':
            plt.scatter(data['x'], (data['x']*0)+(i/1.), c=y_norm, cmap=cm.jet,edgecolor = 'none', norm=matplotlib.colors.LogNorm(vmin=None, vmax=None))
        else:
            plt.scatter(data['x'], (data['x']*0)+(i/1.), c=y_norm, cmap=cm.jet,edgecolor = 'none')
   
        print('%d / %d'%(i,x_f-x_i))
    
    plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    plt.title('DFT Signal')
    plt.xlabel("wavelength (nm)")
    plt.ylabel("Round trip")
    plt.colorbar()
    plt.show()
    
def Plot_stat(x_i, x_f, Nom, delimit, skiphead, extension):
    """
        Trace l histogramme des intensites max
    """
    sns.set_context("talk")
    maxi=[]
    for i in range(x_i,x_f+1):
        data = np.genfromtxt((Nom+'%05d'+extension)%i, delimiter=delimit, skip_header=skiphead, skip_footer=0, names=['x', 'y'])  
        maxi.append(np.max(data['y']))
    NbEvents = x_f - x_i
    plt.hist(maxi,100, log=True, label='Number of events : '+ str(NbEvents))
    plt.legend(frameon=True,loc=2)
    plt.title('Histogram of DFT spectra')
    plt.xlabel("Max intensity")
    plt.ylabel("Number of events")
    plt.show()
    
    
def Plot_Moyenne(x_i, x_f, Nom, delimit, skiphead,offset, extension):
    """
        Trace toutes les courbes
    """
    sns.set_context("talk")

#    Teste premier fichier pr declarer tableau moyenne
    donnees = np.genfromtxt((Nom+'%05d'+extension)%x_i, delimiter=delimit, skip_header=skiphead, skip_footer=0)
    som = [0 for x in range(int(donnees.size/2))]
    Matrix = [[0 for x in range(int(donnees.size/2))] for x in range(x_f+1-x_i)] 
    
#    Recupere toutes les donnes, trace les courbes en scatter et enregistre pr moyenne
    for i in range(x_i,x_f+1):
        data = np.genfromtxt((Nom+'%05d'+extension)%i, delimiter=delimit, skip_header=skiphead, skip_footer=0, names=['x', 'y'])  
        y_norm = (data['y'])
        Matrix[i][:] = y_norm
        data['x']=((data['x'] * 1e9) ) + offset        
        plt.plot(data['x'],y_norm, marker='.',color='c',label='',linewidth=0.0,alpha=0.2) 
        print('%d / %d'%(i,x_f-x_i))

#   Somme puis moyenne de chaque point
    for j in range(x_i,x_f+1):    
        for i in range(int((donnees.size)/2)):
            som[i] = som[i] + Matrix[j][i]
    
    for i in range(int((donnees.size)/2)):   
        som[i] = som[i] / (x_f-x_i)
    
    plt.plot(data['x'],som, marker='',color='k',label='') 
    
    plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    plt.title('DFT Signal')
    plt.xlabel("Time (ns)")
    plt.ylabel("Intensity (a.u.)")
    plt.show()

#==============================================================================
# Execution
#==============================================================================
#Selection fichier
filename = OuvrirFenetreChoix()

#Detection appareil
Appareil = DeviceDetect(filename)

#Edite nom en fonction du nb de digits a retirer
filename = EditNom(filename,Appareil[2])

#Determine echelle a partir de fibre dispersive utilisee
#Res_Fibre =  Fibre_Besancon()
#Res_Fibre =  Fibre_Violette()
Res_Fibre =  Fibre_Lille()

#Plot (Indice initial, Indice final, .., .., Longueur onde centrale, Res_Fibre, offset pour corriger)
Plot_color(0, 3999, filename, Appareil[1], Appareil[0], 1567, Res_Fibre, 2, 'log', Appareil[3])

#Plot histogramme
#Plot_stat(0, 3999, filename, Appareil[1], Appareil[0], Appareil[3])

#Plot moyenne
#Plot_Moyenne(0, 3999, filename, Appareil[1], Appareil[0], 0, Appareil[3])

