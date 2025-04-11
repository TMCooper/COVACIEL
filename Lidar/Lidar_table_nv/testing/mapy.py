import matplotlib.pyplot as plt
import numpy as np
import time
from tableau_test import LidarReader  # Assure-toi que le fichier LidarReader s'appelle lidar.py ou adapte l'import

def polar_plot_loop(lidar):
    plt.ion()
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, polar=True)
    scatter = ax.scatter([], [], c='red', s=5)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rmax(600)  # Ajuste en fonction de ton environnement
    ax.grid(True)

    while True:
        try:
            distances = lidar.get_angle_distance()
            angles_deg = np.arange(360)
            distances_cm = np.array(distances)

            # Filtre les points valides (>0)
            valid = distances_cm > 0
            angles_rad = np.deg2rad(angles_deg[valid])
            dists = distances_cm[valid]

            scatter.set_offsets(np.c_[angles_rad, dists])
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(0.2)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    lidar = LidarReader("/dev/ttyS0")
    lidar.start()

    try:
        polar_plot_loop(lidar)
    finally:
        lidar.stop()
