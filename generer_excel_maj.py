import pandas as pd

# Chemin vers ton fichier original
input_file = r"C:\Users\cdel\OneDrive - Converteo\PROSPECTION\Suivi Prospection CPG.xlsx"
output_file = r"C:\Users\cdel\OneDrive - Converteo\PROSPECTION\Suivi Prospection CPGMAJ.xlsx"

# Charger la feuille FMCG GLOBAL
df = pd.read_excel(input_file, sheet_name="FMCG GLOBAL", engine="openpyxl")

# Exemple de nouveau contact
new_contact = {
    "Prénom": "Clément",
    "Nom": "Delcroix",
    "TOP 40 FMCG": "Groupe Lactalis",
    "Rôle": "Responsable Prospection",
    "Contact envoyé": "O",
    "Contact Accepté O/N": "O",
    "Prospection (O/N)": "O",
    "Retour (O/N)": "N",
    "Next steps": "Suivi personnalisé en cours",
    "Person of interest": "Oui"
}

# Ajouter les colonnes manquantes si besoin
for col in df.columns:
    if col not in new_contact:
        new_contact[col] = None

# Ajouter le contact au tableau
df = pd.concat([df, pd.DataFrame([new_contact])], ignore_index=True)

# Sauvegarder dans un nouveau fichier Excel
df.to_excel(output_file, sheet_name="FMCG GLOBAL", index=False)

print(f"✅ Fichier généré : {output_file}")
