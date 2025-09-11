@echo off
echo Activation de l'environnement virtuel...

:: Se deplace dans le bon dossier de projet
cd "C:\Users\cdel\OneDrive - Converteo\PROSPECTION"

:: Active l'environnement virtuel
call .\prospection_env\Scripts\activate.bat

echo Lancement de l'application CRM...

:: Lance l'application Streamlit
streamlit run Accueil.py