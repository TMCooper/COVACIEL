import threading

# Variable partagée
shared_data = {
    "message": "",
    "ready": False
}

# Verrou pour synchroniser l'accès à la variable partagée
lock = threading.Lock()

# Fonction exécutée dans le thread secondaire
def printer_thread():
    global shared_data
    while True:
        with lock:
            if shared_data["ready"]:
                print("Le thread affiche :", shared_data["message"])
                shared_data["ready"] = False
                break  # On arrête le thread après l'affichage

# Lancer le thread secondaire
t = threading.Thread(target=printer_thread)
t.start()

# Demander à l'utilisateur ce qu'il veut écrire
user_input = input("Que veux-tu afficher ? ")

# Stocker l'entrée utilisateur dans la variable partagée
with lock:
    shared_data["message"] = user_input
    shared_data["ready"] = True

# Attendre que le thread secondaire termine
t.join()
