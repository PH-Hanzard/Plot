# Plot
This repository gathers mainly Python scripts which are about plotting experimental and numerical data.
Requires : Python 2.7 - NumPy - matplotlib - Tkinter - Seaborn

<h2>Scripts :</h2>

<b>Plot_Experimental.py</b> allows to plot easily data from known devices (Oscilloscope, OSA ...)
The device is automatically detected at the file selection. 
For an autocorrelation plot, a polynomial fit is realised to evaluate the FWHM, and then the pulse duration is determined by dividing by the pulse shape factor.

<a href="url"><img src="Images/spectre_osa.png"  height="300" width="450" ></a>

<b>Plot_DFT_Stats.py</b> is made to plot multiple spectra from a known device and/or an intensity distribution histogram

<a href="url"><img src="Images/color.png" height="300" width="450" ></a>


<a href="url"><img src="Images/histo.png" height="300" width="450" ></a>
