@echo off
REM Activer l'environnement virtuel
call "C:\Users\cdel\OneDrive - Converteo\PROSPECTION\prospection_env\Scripts\activate.bat"

REM Lancer le dashboard Streamlit
streamlit run "C:\Users\cdel\OneDrive - Converteo\PROSPECTION\dashboard_prospection.py"
