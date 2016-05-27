# -*- coding: utf-8 -*-
from __future__ import division #Division retourne floating point number
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
from pylab import *
from pylab import pcolor, show, colorbar, xticks, yticks
from Tkinter import Tk
from numpy import corrcoef, sum, log, arange
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
    
def Spectro_Anritsu():
    To_skip = 25
    Delimit = ','
    Couleur = 'r'
    Nom = 'Spectre Optique'
    x = u"Longueur d'onde (nm)"
    y = u'Intensité (Echelle linéaire)'
    Id = 'Spectro_Anritsu'
    coef = 1
    return To_skip, Delimit, Couleur, Nom, x, y, Id,coef
    
def Spectro_2_4():
    To_skip = 30
    Delimit = ','
    Couleur = 'r'
    Nom = 'Spectre Optique'
    x = u"Longueur d'onde (nm)"
    y = u'Intensité (Echelle linéaire)'
    Id = 'Spectro_2_4'
    coef = 1
    return To_skip, Delimit, Couleur, Nom, x, y, Id,coef
    
def DeviceDetect(filename):
    """
        Lit la premiere ligne du fichier pour detecter sa provenance
    """
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
            plt.scatter(data['x'], (data['x']*0)+(i/1.), c=y_norm, cmap=cm.jet,edgecolor = 'none', norm=matplotlib.colors.LogNorm(vmin=None, vmax=1.0368))
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
    
    
def Plot_Moyenne(x_i, x_f, Nom, delimit, skiphead,offset_spect_x,offset_spect_y , facteur_spect, extension,spectrumornot, lambda_centre, Scale):
    """
        Trace toutes les courbes
    """
    sns.set_context("talk")

    fig, ax1 = plt.subplots()
#    Teste premier fichier pr declarer tableau moyenne
    donnees = np.genfromtxt((Nom+'%05d'+extension)%x_i, delimiter=delimit, skip_header=skiphead, skip_footer=0)
    som = [0 for x in range(int(donnees.size/2))]
    Matrix = [[0 for x in range(int(donnees.size/2))] for x in range(x_f+1-x_i)] 
    
#    Recupere toutes les donnes, trace les courbes en scatter et enregistre pr moyenne
    for i in range(x_i,x_f+1):
        data = np.genfromtxt((Nom+'%05d'+extension)%i, delimiter=delimit, skip_header=skiphead, skip_footer=0, names=['x', 'y'])  
        y_norm = (data['y']) 
        Matrix[i][:] = y_norm
#        data['x']=((data['x'] * 1e9) ) + offset
        data['x']=((data['x']* 1e9) / Scale) + lambda_centre  + offset_spect_x       
        ax1.plot(data['x'],y_norm, marker='.',color='c',label='',linewidth=0.0,alpha=0.2) 
        print('%d / %d'%(i,x_f-x_i))

#   Somme puis moyenne de chaque point
    for j in range(x_i,x_f+1):    
        for i in range(int((donnees.size)/2)):
            som[i] = som[i] + Matrix[j][i]
    
    for i in range(int((donnees.size)/2)):   
        som[i] = som[i] / (x_f-x_i)
    
    ax1.plot(data['x'],som, marker='',color='k',label='') 
    
#    Ajout spectre OSA
    
    if spectrumornot == 'spectre':
#        ax2 = ax1.twinx()
        FichierSpectre = OuvrirFenetreChoix()
        Appareil_spectre = DeviceDetect(FichierSpectre)
        result_spectre = RecupData(FichierSpectre,Appareil_spectre)
#        plt.plot(result_spectre[0],result_spectre[1]) 
        ax1.plot(result_spectre[0][:,0],(10**(result_spectre[0][:,1]/20.)*facteur_spect)+offset_spect_y,color='r') 

    

    plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    plt.title('DFT Signal')
    plt.xlabel("Time (ns)")
    plt.ylabel("Intensity (a.u.)")
    plt.show()

def Plot_corr(x_i, x_f, Nom, delimit,Res_fibre, skiphead, extension, lambda_centre, offset):
    donnees = np.genfromtxt((Nom+'%05d'+extension)%x_i, delimiter=delimit, skip_header=skiphead, skip_footer=0)
    Matrix_2 = [[0 for x in range(x_f+1-x_i)] for x in range(int(donnees.size/2))]

    for i in range(x_i,x_f+1):
        data = np.genfromtxt((Nom+'%05d'+extension)%i, delimiter=delimit, skip_header=skiphead, skip_footer=0, names=['x', 'y'])  
        y_norm = (data['y']) 
        for j in range(int(donnees.size/2)):
            Matrix_2[j][i-x_i] = y_norm[j]
        print('%d / %d'%(i,x_f))
    fig, ax = plt.subplots()
    R = corrcoef(Matrix_2)
    R_f = np.rot90(R,2)
    
#pcolormesh mieux que pcolor, plus rapide
    pcolormesh(R_f, cmap='seismic')
#pcolormesh(R_f, cmap='flag')
    colorbar()    
    ticks_x = matplotlib.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format((x*0.1/(abs(Res_Fibre))+1500+offset)))
    ax.xaxis.set_major_formatter(ticks_x)
    ticks_y = matplotlib.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format((x*0.1/(abs(Res_Fibre))+1500+offset)))
    ax.yaxis.set_major_formatter(ticks_y)
    show()
#==============================================================================
# Execution
#==============================================================================
#Ouvre fenetre de dialogue pour le choix du premier fichier a traiter
filename = OuvrirFenetreChoix()

#Detection appareil en fonction de son contenu
Appareil = DeviceDetect(filename)

#Edite nom en fonction du nb de digits a retirer ex :EditNom(C1ph00002.txt,9) -> C1ph
filename = EditNom(filename,Appareil[2])

#Determine echelle a partir de fibre dispersive utilisee
#Res_Fibre =  Fibre_Besancon()
#Res_Fibre =  Fibre_Violette()
Res_Fibre =  Fibre_Lille()

#Plot couleur : (1er fichier, dernier fichier, nom fichier, delimiter, entete a skipper, lambd centre, caract fibre, offset, log ou autre)
Plot_color(0, 200, filename, Appareil[1], Appareil[0], 1567, Res_Fibre, 0, 'loge', Appareil[3])

#Plot histogramme : (1er fichier, dernier fichier, nom fichier, delimiter, entete a skipper, extension)
Plot_stat(0, 200, filename, Appareil[1], Appareil[0], Appareil[3])

#Plot moyenne : (1er fichier, dernier fichier, nom fichier, delimiter, entete a skipper,offset_spect_x,offset_spect_y , facteur_spect, extension, spectre ou pas, lambd centre, res fibre)
Plot_Moyenne(0, 200, filename, Appareil[1], Appareil[0], -6,0.09,0.8, Appareil[3],'sp1ectre', 1567, Res_Fibre)

#Plot_Moyenne(1er fichier, dernier fichier, nom fichier,delimiter,Res_Fibre,entete a skipper, extension, lambda_centre, offset):
Plot_corr(0,200, filename, Appareil[1], Res_Fibre, Appareil[0], Appareil[3], 1550, 2)
