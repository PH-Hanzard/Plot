%Ce script permet la lecture de waveforms simulees par le script d alger. Format classique en colonnes
%Il permet de sortir un histogramme dans un fichier texte
%A regler : FichierEcriture fichierlecture MinPeakHeight 
tic
FichierEcriture='HistoSBS_dell1_r14.txt'  %Forme fichier sortie
%M = dlmread('dell1_r14.dat')
%M = dlmread('dell1_r14.dat','',[0.5e6 0 4e6 1]) 


M = dlmread('dell1_r14.dat','',0.5e6, 0) 

y=M(:,2);
[~,locs_Brillouin] = findpeaks(y,'MinPeakHeight',0.02 ,'MinPeakDistance',0.018e5);
t=1:length(y);

figure(1)
hold on;
plot(t,y,'b');
plot(locs_Brillouin,y(locs_Brillouin),'rv','MarkerFaceColor','r');
grid on;
legend('Signal Oscillo','Pics détectés');
xvalues = 150;
ylabel('Intensity'); xlabel('Time')
title('Alger r14')
hold off;

figure(2)
hold on;
set(gca,'YScale','log')
[n, xout] = hist(y(locs_Brillouin),xvalues);
bar(xout, n,0.5,'b')
ylabel('Number of events'); xlabel('Intensity')
title('Histor14')
%save('ree.mat')

%fid=fopen(FichierEcriture,'a');
fid=fopen(FichierEcriture,'w');
for nbr=1:150
    fprintf(fid,'%d\t,%d\n',n(nbr),xout(nbr));
end
fclose(fid);
toc