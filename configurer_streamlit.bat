@echo off
REM Script: configurer_streamlit.bat
REM Objectif : Vérifier si Python est installé, installer Streamlit, et afficher un message de confirmation

SETLOCAL

REM Définir le dossier de travail
SET "PROSPECTION_DIR=C:\Users\cdel\OneDrive - Converteo\PROSPECTION"
CD /D "%PROSPECTION_DIR%"

REM Vérifier si Python est installé
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH.
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    GOTO END
)

REM Installer Streamlit, pandas et openpyxl
echo ✅ Python détecté. Installation des bibliothèques nécessaires...
python -m pip install --upgrade pip
python -m pip install streamlit pandas openpyxl

REM Vérification de l'installation
streamlit --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ❌ L'installation de Streamlit a échoué.
    GOTO END
)

echo ✅ Streamlit est installé avec succès !
echo Vous pouvez maintenant lancer votre dashboard avec :
echo streamlit run dashboard_prospection.py

:END
ENDLOCAL
pause
