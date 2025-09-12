import pandas as pd
from sqlalchemy import create_engine

# --- PARAMÈTRES ---
EXCEL_FILE_PATH = "../data/Suivi Prospection CPGMAJ.xlsx" # Le nom de votre fichier Excel
SHEET_NAME = "FMCG GLOBAL"                       # Le nom de la feuille à convertir
DB_FILE_PATH = "../data/prospection.db"                  # Le nom de votre future base de données
TABLE_NAME = "contacts"                          # Le nom que vous donnez à la table dans la base

# --- SCRIPT DE CONVERSION ---
print(f"Lecture du fichier Excel '{EXCEL_FILE_PATH}'...")
try:
    # 1. Lire les données de la feuille Excel
    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=SHEET_NAME)

    # 2. Créer une connexion à la base de données SQLite
    # Le fichier .db sera créé automatiquement s'il n'existe pas
    engine = create_engine(f"sqlite:///{DB_FILE_PATH}")

    # 3. Écrire le DataFrame dans une table SQL
    # if_exists='replace' : si la table existe déjà, elle sera écrasée.
    # Utile si vous voulez relancer le script pour mettre à jour.
    df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)

    print("✅ Conversion réussie !")
    print(f"Les données ont été sauvegardées dans le fichier '{DB_FILE_PATH}' dans la table '{TABLE_NAME}'.")

except FileNotFoundError:
    print(f"ERREUR : Le fichier '{EXCEL_FILE_PATH}' n'a pas été trouvé. Vérifiez le nom et l'emplacement.")
except Exception as e:
    print(f"Une erreur est survenue : {e}")