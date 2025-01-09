import os
import shutil

def install_extensions_from_file(file_path="extensions.txt"):
    if not shutil.which("code"):
        print("Visual Studio Code n'est pas installé. Installez-le avant de continuer.")
        return

    if not os.path.exists(file_path):
        print(f"Le fichier {file_path} n'existe pas.")
        return

    with open(file_path, "r") as file:
        extensions = [line.strip() for line in file if line.strip()]
    
    print("Installation des extensions Visual Studio Code...")
    for extension in extensions:
        os.system(f"code --install-extension {extension}")
        print(f"Extension installée : {extension}")

if __name__ == "__main__":
    install_extensions_from_file()