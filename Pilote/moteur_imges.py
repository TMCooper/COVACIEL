import matplotlib
matplotlib.use('Agg')  # Utilisation du backend sans interface graphique

import numpy as np
import matplotlib.pyplot as plt
import time

# Paramètres
periode = 20e-3  # Période de 20ms
rapport_cyclique = 7.5 / 100  # 7.5% de rapport cyclique
temps_haut = rapport_cyclique * periode  # Temps en haut (1.5)
temps_bas = periode - temps_haut  # Temps en bas (0)

# Création du signal
t = np.linspace(0, 2*periode, 1000)  # On génère deux périodes pour voir la répétition
signal = np.zeros_like(t)

# On remplit le signal avec 1.5 sur la période correspondant au temps haut, sinon 0
for i in range(len(t)):
    if (t[i] % periode) < temps_haut:
        signal[i] = 1.5

# Affichage avec matplotlib
plt.figure(figsize=(10, 4))
plt.plot(t * 1000, signal)  # On affiche le temps en ms pour plus de clarté
plt.title("Signal avec rapport cyclique de 7.5%")
plt.xlabel("Temps (ms)")
plt.ylabel("Amplitude")
plt.grid(True)

# Sauvegarde du graphique dans un fichier image
plt.savefig("signal.png")  # Sauvegarde l'image au lieu de l'afficher
print("Graphique sauvegardé sous 'signal.png'")
