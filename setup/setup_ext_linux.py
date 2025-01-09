import os
import shutil
import subprocess
import sys
import tempfile

def install_extensions_from_file(file_path="extensions.txt"):
    # Vérifie si Visual Studio Code est installé
    if not shutil.which("code"):
        print("Visual Studio Code n'est pas installé. Installez-le avant de continuer.")
        return

    # Vérifie si le fichier des extensions existe
    if not os.path.exists(file_path):
        print(f"Le fichier {file_path} n'existe pas.")
        return

    # Lire les extensions à partir du fichier
    with open(file_path, "r") as file:
        extensions = [line.strip() for line in file if line.strip()]

    print("Installation des extensions Visual Studio Code...")

    # Créer un fichier temporaire pour éviter la relance infinie
    temp_file = "/tmp/.no_root_check"
    
    # Vérifier si ce fichier existe pour empêcher la boucle infinie
    if os.geteuid() == 0 and not os.path.exists(temp_file):
        with open(temp_file, 'w') as f:
            f.write("Le script a été relancé sans privilèges root.")

        # Relancer le script sans privilèges root
        print("Vous exécutez ce script avec des privilèges administratifs.")
        print("Relancez-le sans privilèges administratifs...")
        os.execvp(sys.executable, [sys.executable] + sys.argv)
        return

    # Supprimer le fichier temporaire s'il existe
    if os.path.exists(temp_file):
        os.remove(temp_file)

    # Installation des extensions avec les options '--no-sandbox'
    for extension in extensions:
        try:
            # Commande avec les options pour éviter les erreurs de super utilisateur
            subprocess.run(["code", "--install-extension", extension, "--no-sandbox"], check=True)
            print(f"Extension installée : {extension}")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'installation de l'extension {extension} : {e}")
        except Exception as e:
            print(f"Erreur inattendue : {e}")

if __name__ == "__main__":
    install_extensions_from_file()
