import pandas as pd
import numpy as np
import time

# Constantes
LIDAR_CSV_FILE = "../Lidar/lidar_test/lidar_data.csv"
CAMERA_CSV_FILE = "../testcam/out.csv"
DISTANCE_THRESHOLD = 5  # Distance minimale pour éviter un obstacle (en mm)

# Fonction pour lire les données du LiDAR
def read_lidar_data(file):
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        print(f"Erreur lecture LiDAR : {e}")
        return None

# Fonction pour analyser les obstacles avec le LiDAR
def detect_obstacles(lidar_df):
    if lidar_df is not None:
        obstacles = lidar_df[lidar_df["Distance (mm)"] < DISTANCE_THRESHOLD]
        if not obstacles.empty:
            print("Obstacle détecté ! Changer de trajectoire.")
            return True
    return False

# Fonction pour lire les données de la caméra
def read_camera_data(file):
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        print(f"Erreur lecture Caméra : {e}")
        return None

# Fonction pour vérifier l'orientation avec la caméra
def check_orientation(camera_df):
    if camera_df is not None:
        last_frame = camera_df.iloc[-1]  # Dernière capture
        red_detected = last_frame["Red_Detection"]
        green_detected = last_frame["Green_Detection"]
        
        if red_detected and not green_detected:
            print("Trop à droite ! Tourner à gauche.")
            return "left"
        elif green_detected and not red_detected:
            print("Trop à gauche ! Tourner à droite.")
            return "right"
        elif red_detected and green_detected:
            print("Alignement OK.")
            return "straight"
        else:
            print("Aucun bord détecté, vérifier la caméra.")
            return "unknown"
    return "unknown"

# Fonction principale
def main_loop():
    while True:
        lidar_df = read_lidar_data(LIDAR_CSV_FILE)
        camera_df = read_camera_data(CAMERA_CSV_FILE)
        
        obstacle_detected = detect_obstacles(lidar_df)
        direction = check_orientation(camera_df)
        
        if obstacle_detected:
            print("Action : Arrêter ou contourner l'obstacle.")
        else:
            print(f"Action : Continuer en direction {direction}.")
        
        time.sleep(0.5)  # Pause pour éviter surcharge

if __name__ == "__main__":
    main_loop()
