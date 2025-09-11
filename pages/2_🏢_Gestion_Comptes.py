# pages/2_🏢_Gestion_Comptes.py

# pages/2_🏢_Gestion_Compes.py
import streamlit as st
import database as db

st.set_page_config(page_title="Gestion des Comptes", page_icon="🏢")
st.title("🏢 Gestion des Comptes")

# --- Logique pour afficher/masquer le formulaire d'ajout ---
# 1. On initialise une variable en mémoire pour savoir si on doit afficher le formulaire
if 'show_add_compte_form' not in st.session_state:
    st.session_state.show_add_compte_form = False

# 2. On crée le bouton. S'il est cliqué, on inverse l'état d'affichage.
if st.button("➕ Nouveau Compte", type="primary"):
    st.session_state.show_add_compte_form = not st.session_state.show_add_compte_form

# --- Le formulaire d'ajout ne s'affiche que si notre variable est True ---
if st.session_state.show_add_compte_form:
    with st.form("add_compte_form", clear_on_submit=True):
        st.subheader("Ajouter un nouveau compte")
        nom = st.text_input("Nom du nouveau compte")
        statut = st.selectbox("Statut", options=["À qualifier", "Contact établi", "En négociation", "Gagné", "Perdu", "Stand-by"], key="new_statut")
        client_converteo = st.radio("Client Converteo ?", ["O", "N"], key="new_client_status")
        lien_hubspot = st.text_input("Lien Hubspot", key="new_hubspot")
        notes = st.text_area("Notes", key="new_notes")
        
        if st.form_submit_button("Ajouter le compte"):
            db.add_compte(nom, statut, notes, lien_hubspot, client_converteo)
            st.success(f"Compte '{nom}' ajouté !")
            st.session_state.show_add_compte_form = False # On referme le formulaire
            st.rerun()

st.divider()

# --- Section de consultation et modification (inchangée) ---
st.header("Consulter et Modifier un compte existant")
all_comptes = db.get_all_comptes()

if not all_comptes.empty:
    compte_names = {row['nom']: row['id'] for index, row in all_comptes.iterrows()}
    selected_name = st.selectbox("Sélectionnez un compte", options=compte_names.keys())
    
    compte_id = compte_names[selected_name]
    details = db.get_compte_details(compte_id)

    with st.form("update_compte_form"):
        st.write(f"Fiche de **{details['nom']}**")
        nom = st.text_input("Nom", value=details.get('nom', ''))
        
        statut_options = ["À qualifier", "Contact établi", "En négociation", "Gagné", "Perdu", "Stand-by"]
        current_statut = details.get('statut')
        statut_index = statut_options.index(current_statut) if current_statut in statut_options else 0
        statut = st.selectbox("Statut", options=statut_options, index=statut_index)
        
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
    st.warning("Aucun compte à modifier. Ajoutez-en un ci-dessus.")