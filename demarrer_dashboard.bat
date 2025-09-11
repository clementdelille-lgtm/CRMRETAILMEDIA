
@echo off
SETLOCAL

REM Définir le chemin du dossier
SET "PROJET_DIR=C:\Users\cdel\OneDrive - Converteo\PROSPECTION"
SET "PYTHON_SCRIPT=dashboard_prospection.py"
SET "EXCEL_FILE=Suivi Prospection CPG - MAJ.xlsx"

REM Aller dans le dossier
cd /d "%PROJET_DIR%"

REM Vérifier si Python est installé
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ❌ Python n'est pas installé. Veuillez l'installer depuis https://www.python.org/downloads/
    EXIT /B 1
)

REM Installer les bibliothèques nécessaires
echo 📦 Installation des bibliothèques nécessaires...
python -m pip install --upgrade pip
python -m pip install streamlit pandas openpyxl

REM Vérifier que le fichier Python existe
IF NOT EXIST "%PYTHON_SCRIPT%" (
    echo ❌ Le fichier %PYTHON_SCRIPT% est introuvable dans %PROJET_DIR%
    EXIT /B 1
)

REM Vérifier que le fichier Excel existe
IF NOT EXIST "%EXCEL_FILE%" (
    echo ⚠️ Le fichier Excel %EXCEL_FILE% est introuvable. Le dashboard peut ne pas fonctionner correctement.
)

REM Lancer le dashboard Streamlit
echo 🚀 Lancement du dashboard...
streamlit run "%PYTHON_SCRIPT%"

ENDLOCAL
