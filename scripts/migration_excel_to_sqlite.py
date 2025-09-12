# migration_excel_to_sqlite.py
import pandas as pd
from sqlalchemy import create_engine
import sqlite3

# --- PARAMÈTRES ---
EXCEL_FILE = "../data/Suivi Prospection CPGMAJ.xlsx"
DB_FILE = "../data/prospection.db"
COLONNE_COMPTES_EXCEL = "comptes" # Nom de la colonne dans Excel qui contient les noms des comptes

engine = create_engine(f"sqlite:///{DB_FILE}")

def migrate():
    """Script complet pour migrer les données d'Excel vers la base de données SQLite."""
    print("--- Démarrage de la migration ---")

    # 1. Lire les données de l'Excel
    try:
        df_excel = pd.read_excel(EXCEL_FILE, sheet_name="FMCG GLOBAL")
        print(f"✅ 1/5 - Fichier Excel '{EXCEL_FILE}' lu avec succès.")
    except FileNotFoundError:
        print(f"❌ ERREUR : Le fichier '{EXCEL_FILE}' est introuvable.")
        return

    # 2. Préparer et insérer les comptes
    print("Préparation des données 'comptes'...")
    # Garder la première occurrence de chaque compte pour éviter les doublons
    df_comptes_a_inserer = df_excel.drop_duplicates(subset=[COLONNE_COMPTES_EXCEL], keep='first').copy()
    
    # Mapper les noms de colonnes Excel aux noms de colonnes DB pour les comptes
    mapping_comptes = {
        COLONNE_COMPTES_EXCEL: 'nom',
        'Lien Hubspot': 'lien_hubspot', # Assurez-vous que ce nom correspond à votre Excel
        'Client Converteo (O/N)': 'client_converteo' # Assurez-vous que ce nom correspond
    }
    
    # Garder uniquement les colonnes du mapping qui existent vraiment dans le fichier Excel
    colonnes_excel_comptes_existantes = [col for col in mapping_comptes.keys() if col in df_comptes_a_inserer.columns]
    df_comptes_a_inserer = df_comptes_a_inserer[colonnes_excel_comptes_existantes]
    df_comptes_a_inserer.rename(columns=mapping_comptes, inplace=True)

    # Ajouter des colonnes par défaut si elles manquent
    if 'statut' not in df_comptes_a_inserer: df_comptes_a_inserer['statut'] = "Prospect"
    if 'notes' not in df_comptes_a_inserer: df_comptes_a_inserer['notes'] = "Importé depuis Excel"
    if 'lien_hubspot' not in df_comptes_a_inserer: df_comptes_a_inserer['lien_hubspot'] = ""
    if 'client_converteo' not in df_comptes_a_inserer: df_comptes_a_inserer['client_converteo'] = "N"

    print(f"✅ 2/5 - {len(df_comptes_a_inserer)} comptes uniques prêts à être insérés.")
    
    try:
        df_comptes_a_inserer.to_sql("comptes", engine, if_exists='append', index=False)
        print("✅ 3/5 - Nouveaux comptes insérés dans la base de données.")
    except Exception as e:
        print(f"⚠️ 3/5 - Avertissement lors de l'insertion des comptes (ils existent peut-être déjà) : {e}")

    # 4. Récupérer les ID des comptes depuis la BDD pour faire le lien
    with sqlite3.connect(DB_FILE) as con:
        df_comptes_from_db = pd.read_sql("SELECT id, nom FROM comptes", con)
    df_comptes_from_db.rename(columns={'nom': COLONNE_COMPTES_EXCEL}, inplace=True)
    print("✅ 4/5 - ID des comptes récupérés depuis la base de données.")

    # 5. Préparer et insérer les contacts
    print("Préparation des données 'contacts'...")
    df_contacts_a_importer = pd.merge(df_excel, df_comptes_from_db, on=COLONNE_COMPTES_EXCEL, how="left")
    
    # Mapping complet des colonnes Excel vers les colonnes DB pour les contacts
    mapping_contacts = {
        'Prénom': 'prenom', 'Nom': 'nom', 'Rôle': 'role',
        'Contact envoyé': 'contact_envoye', 'Contact Accepté O/N': 'contact_accepte',
        'Prospection (O/N)': 'prospection', 'Retour (O/N)': 'retour',
        'Next steps': 'next_steps', 'Person of interest': 'person_interest',
        'E mail': 'email', # Assurez-vous que ce nom correspond à votre Excel
        'Compte linkedin': 'linkedin', # Assurez-vous que ce nom correspond
        'Dernière Action': 'derniere_action', # Assurez-vous que ce nom correspond
        'id': 'compte_id'
    }
    
    colonnes_db_contacts_existantes = [col for col in mapping_contacts.values() if col in df_contacts_a_importer.rename(columns=mapping_contacts).columns]
    df_contacts_a_importer.rename(columns=mapping_contacts, inplace=True)
    df_contacts_final = df_contacts_a_importer[colonnes_db_contacts_existantes]

    df_contacts_final.to_sql("contacts", engine, if_exists='append', index=False)
    print(f"✅ 5/5 - {len(df_contacts_final)} contacts insérés dans la base de données.")
    print("\n--- Migration terminée avec succès ! ---")

if __name__ == "__main__":
    migrate()