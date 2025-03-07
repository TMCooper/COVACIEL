import matplotlib.pyplot as plt
import math

# Charger les données depuis le fichier
filename = "lidar_data.txt"
angles = []
distances = []

with open(filename, "r") as file:
    for line in file:
        angle, distance = map(float, line.split())
        angles.append(angle)
        distances.append(distance)

# Création du graphique polaire
fig = plt.figure(facecolor='black', figsize=(8, 8))
ax = fig.add_subplot(111, projection='polar')
ax.set_title("Carte polaire LiDAR LD06", fontsize=18, color='cyan')
ax.set_facecolor('navy')
ax.set_ylim([0, max(distances) + 1])
ax.xaxis.grid(True, color='blue', linestyle='dashed')
ax.yaxis.grid(True, color='blue', linestyle='dashed')

# Affichage des points
ax.scatter(angles, distances, c="cyan", s=5)

plt.show()
