<h1 align="center">REPO COVACIEL</h1>

<div align="left">
  <img align="left" src="https://i.imgur.com/fXYKU5q.png" alt="Logo" height="100">
 </div>
 <div align="right">
  <img src="./images/TMCooper_moon.gif" alt="Logo" height="100" width="100">
</div>
<div align="center">
  <picture>
    <source align="top" media="(prefers-color-scheme: dark)" srcset="https://readme-typing-svg.herokuapp.com/?font=Fira+Code&pause=1000&color=00FFFF&multiline=true&random=false&width=435&center=true&lines=Main">
    <img align="top" src="https://readme-typing-svg.herokuapp.com/?font=Fira+Code&pause=1000&color=00FFFF&multiline=true&random=false&width=435&center=true&lines=Main" alt="Typing SVG" />
  </picture>
</div>

<div>
<h1 align="center">Sommaire</h1>
  <ul>
    <li>
      Setup environment
    </li>
    <ul>
      <li>
        <a href="#auto_setup">Auto Setup Environment Windows/Linux</a>
      </li>
      <li>
        <a href="#install_gh">Installing gh</a>
      </li>
      <ul>
        <li>
          <a href="#config_git_global">If you can push after the connection with gh</a>
        </li>
      </ul>
      <li>
        Setup lazygit
      </li>
      <ul>
        <li>
          <a href="#lazygit_install_unbuntu">To install lazygit on ubuntu</a>
        </li>
        <ul>
          <li>
            <a href="#lazygit_install_unbuntu_one_by_one">If the first install methode don't works</a>
          </li>
        </ul>
        <li>
          <a href="#lazygit_install_windows">To install lazygit on Windows</a>
        </li>
      </ul>
    </ul>
    <ul>
      <li>
        Merge commands
      </li>
      <ul>
      <li>
        <a href="#clone_for_one">Clone a specific branch</a>
      </li>
      <li>
        <a href="#clone_all_in_one">Clone all in one command</a>
      </li>
      <li>
        <a href="#merge_method">Merging method</a>
      </li>
      </ul>
        <li>
          <a href="#setup_vscode">Setup VScode</a>
        </li>
      </ul>
      <ul>
        <li>
          <a href="#env_python">Enter environment</a>
        </li>
        <li>
          <a href="#backup">Backup</a>
        </li>
      </ul>
    </ul>
  </ul>
</div>

<div align="center">
  <h1>
    Quest
  </h1>
</div>

- [ ] Incomplete Quest
  - [ ] Création des bases de la class CarControler
  - [ ] Création des bases de la class Camera
  - [ ] Création des bases de la class Lidar
 
- [x] Completed Quest
  - [x] Comprendre le cahier des charges
  - [x] Creation des base de la Classe Pilote

> [!WARNING]
> Vous êtes sur le README.md main.

<h2 id=lazygit_install>To install lazygit on ubuntu</h2>

~~~bash  
sudo apt-get install build-essential libssl-dev libreadline-dev zlib1g-dev
LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
tar xf lazygit.tar.gz lazygit
sudo install lazygit /usr/local/bin
~~~

<h2 id="config_git_global"> Fast config git global</h2>

> [!TIP]
> Si vous avez une erreur au moment de push utiliser les command si dessous et le mots de passe n'est pas obligatoire indiquer le uniquement si votre erreur perciste malgré tous
~~~bash
git config --global user.name "Rias Gremory"
~~~

~~~bash
git config --global user.email "example@gmail.com"
~~~

~~~bash
git config --global user.password "your_password"
~~~

<h2 id="auto_setup">Automatic setup</h2>

__Si c'est une machine Windows__

Lit d'abord le [readme_windows_install.txt](./setup/readme_windows_install.txt) 

> [!TIP]
> fait bien attention a utiliser le fichier [full_setup.ps1](./setup/full_setup.ps1)

__Si c'est une machine Ubuntu__

Dans le cas de Ubuntu il y a juste besoins de rendre le .sh executable dans [readme_linux_install](./setup/readme_linux_install.txt)

> [!TIP]
> Fait bien attention a utiliser cette fois le [full_setup.sh](./setup/full_setup.sh)

<h2 id="install_gh">Install gh</h2>

>[!IMPORTANT]
>Veiller a bien installer gh sous peine de ne pas pouvoir télécharger le repo

__Install :__
~~~bash
sudo apt install gh
~~~

__login :__
~~~bash
gh auth login
~~~

__Logout :__
~~~bash
gh auth logout
~~~

</br>

## How to clone the repo
- go where you want to download the repo
- open cmd (CTRL + ALT + T)
- type :
~~~bash
git clone https://github.com/TMCooper/Devel.git
~~~

# Create you own branch to push your code
- Open lazygit on your terminal (but in the folder you cloned befor)
- Go on the local branches (use the arrow right and left to change the window and up and down for file)
- Then on the local branches press n (not on capital letter)
- Enter the name of the branche like ``Younes`` or ``Camille``
- Then select the branche (if is not the case and press space bar to select the branch where you push your own code)
- And juste select what file you edit or some other thing and push on your Branch

<h1 id=lazygit_install_unbuntu_one_by_one>If the big installation don't work try one by one</h1>

~~~bash
LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | \grep -Po '"tag_name": *"v\K[^"]*')
~~~

~~~bash
curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/download/v${LAZYGIT_VERSION}/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
~~~

~~~bash
tar xf lazygit.tar.gz lazygit
~~~

~~~bash
sudo install lazygit -D -t /usr/local/bin/
~~~

## Clone specific branch

__pre-release__
~~~bash
git clone -b pre-release --single-branch https://github.com/TMCooper/COVACIEL.git
~~~

<h1 id="setup_vscode">Setup VScode</h1>

>[!NOTE]
>Of course clone your branch or the repo to use the command
- If you want to setup quickly, you can use the [install_extensions.py](./setup/extention_auto_installer/install_extensions.py) with the following command :
~~~bash
cd /setup/extention_auto_installer
~~~
>[!WARNING]
>The command changes between Windows and Linux
>For Windows : 
>~~~bash
>python install_extensions.py
>~~~
>For Linux : 
>~~~bash
>python3 install_extensions.py
>~~~

<h1 id=lazygit_install_windows>Install git on windows</h1>
>[!IMPORTANT]
> Veiller a bien installer gh sous peine de ne pas pouvoir télécharger le repo

- Open ``CMD`` or ``powershell``
- Type this command : 

~~~powershell
winget install -e --id Git.Git
~~~
- After the previous command type :
~~~powershell
winget install -e --id GitHub.cli
~~~

- And now you can login on your windows device

### install Chocolatey 

- execute powershell in administrator
- copy and pasth this line on your powershell :
~~~powershell 
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
~~~
- tap on the same powershell (or you can reopen an new but in administrator too) 
~~~bash
choco install lazygit
~~~

>[!NOTE]
> You can also use the sript installer to do all at your place : [installer.bat](./setup/auto_install_lazygit_and_gh/installer.bat)

<h2 id="clone_for_one">Git clone Branch</h2>

__TMCooper__
~~~bash
git clone -b TMCooper --single-branch https://github.com/TMCooper/COVACIEL.git
~~~

__pre-release__
~~~bash 
git clone -b pre-release --single-branch https://github.com/TMCooper/COVACIEL.git
~~~

__Main branch__
~~~bash
git clone -b main --single-branch https://github.com/TMCooper/COVACIEL.git
~~~

<h2 id="merge_method">Merge command</h2>

__First__
- git checkout pour basculer vers la branche dans laquelle vous souhaitez fusionner

~~~bash
git checkout pre-merged
~~~

- check with
~~~bash
git branch
~~~

__Merge vers main__
~~~bash
git checkout main
~~~

~~~bash
git merge pre-merged
~~~

## Récupération de la branch pre-merged et main
~~~bash
git fetch origin pre-release:pre-release
~~~~

~~~bash
git fetch origin main:main
~~~

>[!WARNING]
>Ne pas oublie de pull indivituellement chaque branche pour que les connection sois bonne puis merge

<h2 id="clone_all_in_one">Clone avec toute les branch</h2>

~~~bash
git clone https://github.com/TMCooper/COVACIEL.git && cd COVACIEL/ && git fetch origin pre-release:pre-release && git fetch origin TMCooper:TMCooper
~~~

>[!NOTE]
>Pull all branches juste après !

<h2 id=backup>Make Bakup with tag</h2>

> [!NOTE]
> v1 est un tag qui varie et qui ne dois jamais être le même

__1. Basculer sur la branche principale__
~~~bash
git checkout main
~~~

__2. Créer un tag avant la fusion__
~~~bash
git tag -a "v1" -m "$Point de restauration avant la fusion de pre-release"
~~~

__3. Pousser le tag vers le dépôt distant__
~~~bash
git push origin "v1"
~~~

__4. Fusionner la branche pre-release dans main__
~~~bash
git merge pre-release
~~~

__5. Pousser la fusion__
~~~bash
git push origin main
~~~

<h2 id=env_python>Python Env</h2>

> [!TIP]
> Création d'un env python : 
> sous Ubuntu : python3 -m venv COVACIEL
> sous Windows : python -m venv COVACIEL

Activate l'env python

__Windows__
~~~bash
.\COVACIEL\Scripts\activate
~~~

__Linux__
~~~bash
source COVACIEL/bin/activate
~~~

> [!NOTE]
> Avoir un environement qui ne change pas limite les problèmes de copatibilité sur la machine pendant les developpements les dependances contenue dans le requirements devrons donc être installer dedans

<h2>Backup automation</h2>

> [!TIP]
> L'automatisation de la backup du code source fonctionne

Le script est la : [git_backup.py](./backup_automate/git_backup.py)

<h1>README.md</h1>

>[!IMPORTANT]
>README.md fait par TMCooper
