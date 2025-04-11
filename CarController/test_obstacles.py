import random

class DummyLidar:
    def __init__(self):
        # Simule des mesures sous la forme (angle, distance, confiance)
        self.measurements = self._generate_fake_data()

    def _generate_fake_data(self):
        data = []
        for angle in range(360):
            if angle == 90:
                dist = random.randint(100, 800)  # obstacle à droite
            elif angle == 270:
                dist = random.randint(100, 800)  # obstacle à gauche
            else:
                dist = random.randint(500, 2000)
            confidence = random.randint(0, 255)
            data.append((angle, dist, confidence))
        return data

def check_obstacles(measurements):
    distances = {90: None, 270: None}
    for angle, dist, _ in measurements:
        if angle == 90:
            distances[90] = dist
        elif angle == 270:
            distances[270] = dist

    print(f"📏 Distance droite (90°): {distances[90]} mm")
    print(f"📏 Distance gauche (270°): {distances[270]} mm")

    seuil = 300  # mm

    if distances[90] is not None and distances[90] < seuil:
        print("🧱 Obstacle à droite → Aller à gauche")
        return "left"
    elif distances[270] is not None and distances[270] < seuil:
        print("🧱 Obstacle à gauche → Aller à droite")
        return "right"
    
    print("✅ Pas d'obstacle proche → Tout droit")
    return "straight"

if __name__ == "__main__":
    lidar = DummyLidar()
    decision = check_obstacles(lidar.measurements)
    print(f"🧭 Décision finale : {decision}")
