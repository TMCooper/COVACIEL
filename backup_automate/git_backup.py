import subprocess
import datetime

# Variables
BRANCH_NAME = "main"
PRE_RELEASE_BRANCH = "pre-release"
TAG_NAME = f"v{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}"
TAG_MESSAGE = "Point de restauration avant la fusion de pre-release"

# Fonction pour exécuter une commande shell et vérifier son succès
def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
        print(f"Commande réussie: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande: {command}")
        print(e)

# 1. Basculer sur la branche principale
run_command(f"git checkout {BRANCH_NAME}")

# 2. Créer un tag avant la fusion
run_command(f"git tag -a {TAG_NAME} -m \"{TAG_MESSAGE}\"")

# 3. Pousser le tag vers le dépôt distant
run_command(f"git push origin {TAG_NAME}")

# 4. Fusionner la branche pre-release dans main
run_command(f"git merge {PRE_RELEASE_BRANCH}")

# 5. Pousser la fusion
run_command(f"git push origin {BRANCH_NAME}")
