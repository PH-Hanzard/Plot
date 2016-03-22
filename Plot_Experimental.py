# -*- coding: utf-8 -*-
from __future__ import division #Division retourne floating point number
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from Tkinter import Tk
from tkFileDialog import askopenfilename
from scipy.interpolate import splrep, sproot
#==============================================================================
# 24 fevrier 2016
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
    
def Oscillo_LeCroy():
    To_skip = 6
    Delimit = ','
    Couleur = 'k'
    Nom = 'Trace temporelle'
    x = 'Temps (us)'
    y =  u'Intensité (u.a.)'
    Id = 'Oscillo_LeCroy'
    coef = 1e6
    return To_skip, Delimit, Couleur, Nom, x, y, Id,coef
    
def RF_RohdeSchwarz():
    To_skip = 30
    Delimit = ';'
    Couleur = 'g'
    Nom = u'Spectre Radiofréquence'
    x = u'Fréquence (MHz)'
    y = u'Intensité (dBm)'
    Id = 'RF_RohdeSchwarz'
    coef = 1e-6
    return To_skip, Delimit, Couleur, Nom, x, y, Id,coef
    
def Oscillo_autoco():
    To_skip = 4
    Delimit = ';'
    Couleur = 'b'
    Nom = u'Autocorrélation'
    x = 'Temps de retard (ps)'
    y = u'Intensité (u.a.)'
    Id = 'Oscillo_autoco'
    coef = 1
    
    return To_skip, Delimit, Couleur, Nom, x, y, Id,coef
    
def normalize(fct):
    """
        Set function's maximum at 1
    """
    return (fct/max(fct))

def OuvrirFenetreChoix():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    return filename

def Plot(x,y,couleur,titre,xlabel,ylabel,Appareil,K,scale,coef):
    """
        Trace la fonction. Dans le cas d une autoco, un fit polynomial est realise, puis la
        duree reele FWHM de limpulsion est determinee par division par k
    """
    print('k : ',K)
    sns.set_style("ticks")
    ax = plt.axes()
    plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    Legende = ''
    sns.set_context("poster")
#    sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5})
    plt.title(titre, fontweight='bold', y=1.05)
    plt.xlabel(xlabel, fontsize=18)

    
    if Appareil[6] == 'Oscillo_autoco':
        FWHM = fwhm(x,y,10)
        print('FWHM : ',(FWHM))
        ax.arrow(-4*FWHM, 0.5, 3*FWHM, 0, head_width=0.03, head_length=2, fc='r', ec='k')
        ax.arrow(4*FWHM, 0.5, -3*FWHM, 0, head_width=0.03, head_length=2, fc='r', ec='k')
        Tps_reel = FWHM/K
        Legende = '%f'%Tps_reel
        plt.plot(x,y,marker='',color=couleur,label=r'$\Delta \tau=$'+str(K)+r'$\times $'+Legende+'ps')
        plt.legend(frameon=True,loc=2)
    else:
        if scale == 'log':
            plt.ylabel('Intensite (dB)',fontsize=18)
            plt.plot(x*coef,10*np.log10(y),marker='',color=couleur,label='')

        else:
            plt.plot(x*coef,y,marker='',color=couleur,label='')
            plt.ylabel(ylabel, fontsize=18)
    ax.tick_params(axis='x', labelsize=18)
    ax.tick_params(axis='y', labelsize=18)
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
        return recup
    else:
        recup = np.genfromtxt(filename, delimiter=Appareil[1], skip_header=Appareil[0], skip_footer=0)     
        return recup

def Autoco(Appareil,recup,conv_factor,base,cases,shape):
    if shape == 'gauss':
        K = 1.41
    elif shape == 'sech':
        K = 1.55

    if Appareil[6] == 'Oscillo_autoco':
        NbPts = recup[0]
        datay = normalize(recup[4:])
        x=[]
        for i in range(0,datay.size):
           x.append((float(i)*cases*conv_factor*base/NbPts)) 
        x = np.asarray(x)

        #Recherche max et met a zero
        abscisse_max = datay.argmax()
        x_norm = x - x[abscisse_max]     
        
        data=np.array([x_norm,datay]).T
        return data, K
    else:
        return recup, K
        
        

def fwhm(x, y, k=10):
    """
    Determine full-with-half-maximum of a peaked set of points, x and y.
    Assumes that there is only one peak present in the datasset.  The function
    uses a spline interpolation of order k.
    """

    class MultiplePeaks(Exception): pass
    class NoPeaksFound(Exception): pass

    half_max = np.amax(y)/2.0
    s = splrep(x, y - half_max)
    roots = sproot(s)

    if len(roots) > 2:
        raise MultiplePeaks("The dataset appears to have multiple peaks, and "
                "thus the FWHM can't be determined.")
    elif len(roots) < 2:
        raise NoPeaksFound("No proper peaks were found in the data set; likely "
                "the dataset is flat (e.g. all zeros).")
    else:
        return abs(roots[1] - roots[0])
    
    

#==============================================================================
# Programme  :
#==============================================================================
#   Ouvre la fenetre de choix du fichier a traiter
filename = OuvrirFenetreChoix()

#Lit la premiere ligne du fichier pour en determiner la provenance
Appareil = DeviceDetect(filename)

#   Recupere les donnees en fonction de l appariel 
data = RecupData(filename,Appareil)

#Traite dans le cas d une autocorrelation - ne fait rien sinon
# Parametres : Appareil,data,Nb cases ; facteur conversion ps/ms ; tps/div en ms : gauss ou sech
result = Autoco(Appareil,data,29.5,1,10,'gauss')

#   Trace
Plot(result[0][:,0],result[0][:,1], Appareil[2], Appareil[3], Appareil[4], Appareil[5],Appareil,result[1],'logg',Appareil[7])

