# pages/2_🏢_Gestion_Comptes.py

import streamlit as st
import database as db

st.title("🏢 Gestion des Comptes")

# Définir les étapes du funnel ici pour les réutiliser
FUNNEL_STAGES = ["À qualifier", "Contact établi", "En négociation", "Gagné", "Perdu", "Stand-by"]

# --- Section Modification ---
st.header("Modifier un compte existant")
all_comptes = db.get_all_comptes()

if not all_comptes.empty:
    # ... (le code pour sélectionner le compte reste le même) ...
    compte_names = {row['nom']: row['id'] for index, row in all_comptes.iterrows()}
    selected_name = st.selectbox("Sélectionnez un compte à modifier", options=compte_names.keys())
    
    compte_id = compte_names[selected_name]
    details = db.get_compte_details(compte_id)

    with st.form("update_compte_form"):
        st.write(f"Modification de **{details['nom']}**")
        nom = st.text_input("Nom", value=details.get('nom', ''))
        
        # *** CHANGEMENT ICI ***
        # Utiliser la liste standardisée pour le statut
        current_statut = details.get('statut')
        statut_index = FUNNEL_STAGES.index(current_statut) if current_statut in FUNNEL_STAGES else 0
        statut = st.selectbox("Statut", options=FUNNEL_STAGES, index=statut_index)
        
        # ... (le reste du formulaire reste le même) ...
        client_converteo_options = ["O", "N"]
        current_client_status = details.get('client_converteo', 'N')
        client_converteo = st.radio("Client Converteo ?", client_converteo_options, index=client_converteo_options.index(current_client_status))
        lien_hubspot = st.text_input("Lien Hubspot", value=details.get('lien_hubspot', ''))
        notes = st.text_area("Notes", value=details.get('notes', ''))
        
        if st.form_submit_button("Enregistrer les modifications"):
            db.update_compte(compte_id, nom, statut, notes, lien_hubspot, client_converteo)
            st.success("Compte mis à jour !")
            st.rerun()

else:
    st.warning("Aucun compte à modifier. Ajoutez-en un ci-dessous.")

# --- Section Ajout ---
with st.expander("➕ Ajouter un nouveau compte"):
    with st.form("add_compte_form", clear_on_submit=True):
        nom = st.text_input("Nom du nouveau compte")
        
        # *** CHANGEMENT ICI ***
        # Utiliser la liste standardisée pour le statut
        statut = st.selectbox("Statut", options=FUNNEL_STAGES, key="new_statut")
        
        # ... (le reste du formulaire reste le même) ...
        client_converteo = st.radio("Client Converteo ?", ["O", "N"], key="new_client_status")
        lien_hubspot = st.text_input("Lien Hubspot", key="new_hubspot")
        notes = st.text_area("Notes", key="new_notes")
        
        if st.form_submit_button("Ajouter le compte"):
            db.add_compte(nom, statut, notes, lien_hubspot, client_converteo)
            st.success(f"Compte '{nom}' ajouté !")
            st.rerun()