import threading
import time

# Variable partagée
control_car = 0
lock = threading.Lock()
running = True  # Pour arrêter le thread proprement

def adjust_speed():
    global control_car
    while running:
        with lock:
            control_car
            print(f"[THREAD] Ajustement de la vitesse avec la valeur : {control_car}")
        time.sleep(1)

def update_control_car(new_value):
    global control_car
    with lock:
        control_car = new_value
    print(f"[MAIN] control_car mis à jour : {new_value}")

# Lancer le thread
t = threading.Thread(target=adjust_speed)
t.start()

# Mise à jour de la variable (simulation)
update_control_car(10)
time.sleep(2)

# Arrêter proprement le thread
running = False
t.join()

print("Fin du programme.")
