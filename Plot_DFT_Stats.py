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
import scipy.constants as cte

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


def RecupData(filename,Appareil):
    if Appareil[6] == 'Oscillo_autoco':
        recup = np.loadtxt(filename, skiprows=0)
        return recup
    else:
        recup = np.genfromtxt(filename, delimiter=Appareil[1], skip_header=Appareil[0], skip_footer=0)     
        return recup, 1
    
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
    """
        En dBm : mW = 10 ^ (dBm/10) dBm and dBW
        are defined by forming the ratio of the power you want to express relative
        to a reference power, which is
        1 W for dBW and 1 mW for dBm. 
    """
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
#    Longueur = 1
#    D = - 429
#    return Longueur * D * 1e-3
#    Beta_2_L = 546e-24
    Beta_2_L = 630e-24
    Beta_3_L = -3.8e-36
    return Beta_2_L,Beta_3_L
    
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
  

#==============================================================================
# Mapping      
#==============================================================================
        omega_0 = 2 * np.pi * cte.c / (lambda_centre)   
        
        A = Scale[1] / 2
        B = Scale[0]
#        On centre en t=0
        T = data['x'] - np.min(data['x']) - ((np.max(data['x'])-np.min(data['x']))/2) 
        
        B2 = (-2*A*omega_0) + B    
        C = (A*(omega_0**2)) - (B*omega_0) - T
        
        
        Delta = (B2**2) - (4*A*C)
        
        omega1 = (-B2 + np.sqrt(Delta) ) / (2*A)
        
        Lambdd1 = 2 * np.pi * cte.c / omega1    
    
    
        if LogOrLin == 'log':
            plt.scatter(Lambdd1*1e9, (Lambdd1*0)+(i/1.), c=y_norm, cmap=cm.jet,edgecolor = 'none', norm=matplotlib.colors.LogNorm(vmin=None, vmax=1.0368))
        else:
            plt.scatter(Lambdd1*1e9, (Lambdd1*0)+(i/1.), c=y_norm, cmap=cm.jet,edgecolor = 'none')    


##
#        data['x']=((data['x'] * 1e9) / -0.429) + lambda_centre + offset
#        if LogOrLin == 'log':
#            plt.scatter(data['x'], (data['x']*0)+(i/1.), c=y_norm, cmap=cm.jet,edgecolor = 'none', norm=matplotlib.colors.LogNorm(vmin=None, vmax=1.0368))
#        else:
#            plt.scatter(data['x'], (data['x']*0)+(i/1.), c=y_norm, cmap=cm.jet,edgecolor = 'none')
#   
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
    
    
def Plot_Moyenne(x_i, x_f, Nom, delimit, skiphead, extension,spectrumornot, lambda_centre, Scale,facteur_spect,offset_spect_y):
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
        Matrix[i-x_i][:] = y_norm
#        data['x']=((data['x'] * 1e9) ) + offset
        
#==============================================================================
# Conversion lambda omega et calcul mapping dispersion        
#==============================================================================

        omega_0 = 2 * np.pi * cte.c / (lambda_centre)   
        
        A = Scale[1] / 2
        B = Scale[0]
#        On centre en t=0
        T = data['x'] - np.min(data['x']) - ((np.max(data['x'])-np.min(data['x']))/2) 
        
        B2 = (-2*A*omega_0) + B    
        C = (A*(omega_0**2)) - (B*omega_0) - T
        
        
        Delta = (B2**2) - (4*A*C)
        
        omega1 = (-B2 + np.sqrt(Delta) ) / (2*A)
        
        Lambdd1 = 2 * np.pi * cte.c / omega1
    
    
        
#        data['x']=((data['x']* 1e9) / Scale) + lambda_centre  + offset_spect_x       
        ax1.plot(Lambdd1*1e9,y_norm, marker='.',color='c',label='',linewidth=0.0,alpha=0.2) 
        print('%d / %d'%(i,x_f-x_i))

#   Somme puis moyenne de chaque point
    for j in range(x_i,x_f+1):    
        for i in range(int((donnees.size)/2)):
            som[i] = som[i] + Matrix[j-x_i][i]
    
    for i in range(int((donnees.size)/2)):   
        som[i] = som[i] / (x_f-x_i)
    
    ax1.plot(Lambdd1*1e9,som, marker='',color='k',label='') 
    
#    Ajout spectre OSA
    
    if spectrumornot == 'spectre':
#        ax2 = ax1.twinx()
        FichierSpectre = OuvrirFenetreChoix()
        Appareil_spectre = DeviceDetect(FichierSpectre)
        result_spectre = RecupData(FichierSpectre,Appareil_spectre)
#        plt.plot(result_spectre[0],result_spectre[1]) 
        ax1.plot(result_spectre[0][:,0],((10**(result_spectre[0][:,1]/10.))*facteur_spect)+offset_spect_y,color='r') 
#        ax1.plot(result_spectre[0][:,0],(10**(result_spectre[0][:,1]/10.)),color='r') 


    plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    plt.title('DFT Signal')
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (a.u.)")
    plt.show()

def Plot_corr(x_i, x_f, Nom, delimit,Scale, skiphead, extension, lambda_centre):
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
    
    
#    Mapping
    omega_0 = 2 * np.pi * cte.c / (lambda_centre)   
        
    A = Scale[1] / 2
    B = Scale[0]
#        On centre en t=0
    T = data['x'] - np.min(data['x']) - ((np.max(data['x'])-np.min(data['x']))/2) 
    
    B2 = (-2*A*omega_0) + B    
    C = (A*(omega_0**2)) - (B*omega_0) - T
    
    
    Delta = (B2**2) - (4*A*C)
    
    omega1 = (-B2 + np.sqrt(Delta) ) / (2*A)
    
    Lambdd1 = 2 * np.pi * cte.c / omega1    
    l = np.linspace(0,0,1000)

#On augmente la longueur du tableau en ajoutant des 0 pour  les pbs de 'out of bounds' sur la partie externe du plot
    lambdd1 = np.concatenate((l,Lambdd1))
    
#pcolormesh mieux que pcolor, plus rapide
    pcolormesh(R_f, cmap='seismic')
#pcolormesh(R_f, cmap='flag')
    colorbar()    
#    On part de la fin du tableau car tps oppose a longueur d onde
    ticks_x = matplotlib.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(lambdd1[lambdd1.size-x-1]*1e9))
    ax.xaxis.set_major_formatter(ticks_x)
    ticks_y = matplotlib.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(lambdd1[lambdd1.size-x-1]*1e9))
    ax.yaxis.set_major_formatter(ticks_y)    
    
#    ticks_x = matplotlib.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format((x*0.1/(abs(-0.429))+1500+offset)))
#    ax.xaxis.set_major_formatter(ticks_x)
#    ticks_y = matplotlib.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format((x*0.1/(abs(-0.429))+1500+offset)))
#    ax.yaxis.set_major_formatter(ticks_y)
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
Plot_color(0, 500, filename, Appareil[1], Appareil[0], 1573e-9, Res_Fibre, 323, 'loge', Appareil[3])

#Plot histogramme : (1er fichier, dernier fichier, nom fichier, delimiter, entete a skipper, extension)
Plot_stat(0, 100, filename, Appareil[1], Appareil[0], Appareil[3])

#Plot moyenne : (1er fichier, dernier fichier, nom fichier, delimiter, entete a skipper,offset_spect_x,offset_spect_y , facteur_spect, extension, spectre ou pas, lambd centre, res fibre)
Plot_Moyenne(0, 100, filename, Appareil[1], Appareil[0], Appareil[3],'spectre', 1573e-9, Res_Fibre,5,0.07)

#Plot_corr(1er fichier, dernier fichier, nom fichier,delimiter,Res_Fibre,entete a skipper, extension, lambda_centre, offset):
Plot_corr(0,500, filename, Appareil[1], Res_Fibre, Appareil[0], Appareil[3], 1573e-9)
