#!/bin/bash

# Vérifie si le script est exécuté en tant qu'administrateur (root)
if [ "$(id -u)" -ne 0 ]; then
    echo "Ce script nécessite des droits administratifs."
    echo "Relancement du script avec des privilèges administratifs..."
    sudo "$0" "$@"
    exit 1
fi

# Update the system
echo "Mise à jour du système..."
sudo apt update -y
sudo apt upgrade -y

# Installation de curl
echo "Installation de curl..."
sudo apt install -y curl

# Installation de Git et GitHub CLI via apt-get (pour Debian/Ubuntu)
echo "Installation de Git..."
sudo apt install -y git

echo "Installation de GitHub CLI..."
sudo apt install -y gh

# Installation de Python pour l'utilisateur uniquement via apt-get
echo "Installation de Python 3.10..."
sudo apt install -y python3.10 python3.10-venv python3.10-dev
sudo apt install python3-pip -y

# Installation de Visual Studio Code (VSCode) via apt
echo "Installation de Visual Studio Code..."
sudo apt install software-properties-common apt-transport-https wget -y
wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main"
sudo apt install code -y

# Ajout de Python au PATH utilisateur
echo "Ajout de Python au PATH..."
USER_PATH="$HOME/.bashrc"
echo "export PATH=\$PATH:/usr/local/bin/python3.10" >> "$USER_PATH"
source "$USER_PATH"

# Exécution du script Python pour installer les extensions
echo "Exécution du script Python pour installer les extensions..."
# Lancement du script python sans privilèges administratifs
sudo -u $SUDO_USER python3 setup_ext_linux.py

# Installation de LazyGit manuellement
echo "Installation de LazyGit..."

# 1. Récupérer la dernière version de LazyGit via l'API GitHub
LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": *"v\K[^"]*')

# 2. Télécharger le tar.gz de LazyGit
curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/download/v${LAZYGIT_VERSION}/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"

# 3. Extraire l'archive tar.gz
tar xf lazygit.tar.gz lazygit

# 4. Installer LazyGit dans /usr/local/bin
sudo install lazygit -D -t /usr/local/bin/

# Nettoyer les fichiers temporaires
rm lazygit.tar.gz

echo "LazyGit installé avec succès !"
