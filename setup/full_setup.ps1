# Vérifie si le script est exécuté en tant qu'administrateur
$adminCheck = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$scriptPath = Split-Path -Path $PSCommandPath  # Récupère le chemin du script courant

if (-not $adminCheck.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Ce script nécessite des droits administratifs."
    Write-Host "Relancement du script avec des privilèges administratifs..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File $PSCommandPath" -Verb RunAs
    exit
}

# Déplacement explicite dans le répertoire du script
Set-Location $scriptPath

# Installation de Git et GitHub CLI via winget
Write-Host "Installation de Git..."
winget install -e --id Git.Git
Write-Host "Installation de GitHub CLI..."
winget install -e --id GitHub.cli

# Installation de Visual Studio Code via winget
Write-Host "Installation de Visual Studio Code..."
winget install Microsoft.VisualStudioCode --scope machine

# Exécution du script Python pour installer les extensions
Write-Host "Exécution du script Python pour installer les extensions..."
Write-Host "Répertoire courant : $(Get-Location)"
if (Test-Path "setup_ext.py") {
    Write-Host "Le fichier setup_ext.py existe."
    python ./setup_ext.py
} else {
    Write-Host "Le fichier setup_ext.py n'existe pas dans le répertoire courant."
}

# Installation de Chocolatey via PowerShell
Write-Host "Installation de Chocolatey..."
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Installation de LazyGit via Chocolatey
Write-Host "Installation de LazyGit..."
choco install lazygit
