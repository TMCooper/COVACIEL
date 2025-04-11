import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from tableau_test import LidarReader

class LidarMap:
    def __init__(self, lidar: LidarReader, max_range=5.0):
        self.lidar = lidar
        self.max_range = max_range
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.sc = self.ax.scatter([], [], s=10, c='blue', alpha=0.7)

        self.ax.set_xlim(-max_range, max_range)
        self.ax.set_ylim(-max_range, max_range)
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_title("Carte LIDAR LD06 - Vue cartésienne")
        self.ax.grid(True)
        self.ax.set_aspect('equal')

    def update(self, frame):
        points = self.lidar.get_points()
        if not points:
            return self.sc,

        xs = [p.distance * np.cos(np.radians(p.angle)) for p in points]
        ys = [p.distance * np.sin(np.radians(p.angle)) for p in points]
        self.sc.set_offsets(np.c_[xs, ys])
        return self.sc,

    def run(self):
        ani = animation.FuncAnimation(self.fig, self.update, interval=100, blit=True)
        plt.show()


