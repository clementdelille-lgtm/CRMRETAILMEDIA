# pages/2_🏢_Gestion_Comptes.py
import streamlit as st
import database as db
import pandas as pd

st.set_page_config(page_title="Gestion des Comptes", page_icon="🏢")
st.title("🏢 Gestion des Comptes")

# --- Logique pour afficher/masquer le formulaire d'ajout ---
if 'show_add_compte_form' not in st.session_state:
    st.session_state.show_add_compte_form = False

if st.button("➕ Nouveau Compte", type="primary"):
    st.session_state.show_add_compte_form = not st.session_state.show_add_compte_form
    if 'compte_to_delete' in st.session_state:
        del st.session_state.compte_to_delete

# --- Le formulaire d'ajout ne s'affiche que si notre variable est True ---
if st.session_state.show_add_compte_form:
    with st.form("add_compte_form", clear_on_submit=True):
        st.header("Ajouter un Compte")
        nom = st.text_input("Nom de l'entreprise *")
        
        c1, c2 = st.columns(2)
        with c1:
            statut = st.selectbox("Statut", options=["À qualifier", "En cours", "Opportunité", "Client", "Fermé/Perdu"])
        with c2:
            client_converteo = st.selectbox("Client Converteo ?", options=["Oui", "Non"])
            
        lien_hubspot = st.text_input("Lien Hubspot")
        notes = st.text_area("Notes sur le compte")
        
        # Le bouton de soumission est ESSENTIEL à l'intérieur du formulaire
        if st.form_submit_button("Créer le compte", use_container_width=True):
            if nom:
                db.add_compte(nom, statut, notes, lien_hubspot, client_converteo)
                st.success(f"Le compte '{nom}' a été créé !")
                st.session_state.show_add_compte_form = False
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Le nom de l'entreprise est obligatoire.")
    
st.divider()

# --- Section de consultation et de suppression ---
st.header("Consulter et Modifier un Compte")
all_comptes = db.get_all_comptes()

if not all_comptes.empty:
    compte_names = {row['nom']: row['id'] for index, row in all_comptes.iterrows()}
    
    selected_compte_name = st.selectbox("Choisissez un compte", options=compte_names.keys(), key="view_compte")
    selected_compte_id = compte_names[selected_compte_name]
    
    details = db.get_compte_details(selected_compte_id)
    contacts_df = db.get_contacts_for_compte(selected_compte_id)

    # --- FICHE COMPTE COMPLÈTE ---
    with st.form("fiche_compte_form"):
        st.subheader(f"📝 Fiche de {details.get('nom')}")

        c1, c2 = st.columns(2)
        with c1:
            nom_update = st.text_input("Nom de l'entreprise", value=details.get('nom'))
            
            # Correction de l'erreur pour les valeurs de statut inexistantes
            status_options = ["À qualifier", "En cours", "Opportunité", "Client", "Fermé/Perdu"]
            current_status = details.get('statut')
            if current_status not in status_options:
                status_index = 0
            else:
                status_index = status_options.index(current_status)

            statut_update = st.selectbox(
                "Statut",
                options=status_options,
                index=status_index
            )

        with c2:
            lien_hubspot_update = st.text_input("Lien Hubspot", value=details.get('lien_hubspot', ''))
            
            client_converteo_options = ["Oui", "Non"]
            current_client = details.get('client_converteo')
            if current_client not in client_converteo_options:
                client_index = 1
            else:
                client_index = client_converteo_options.index(current_client)
            
            client_converteo_update = st.selectbox(
                "Client Converteo ?",
                options=client_converteo_options,
                index=client_index
            )
        
        notes_update = st.text_area("Notes", value=details.get('notes', ''))
        
        # --- Boutons d'action ---
        col1_btn, col2_btn = st.columns([3, 1])
        with col1_btn:
            if st.form_submit_button("💾 Enregistrer les modifications", use_container_width=True, type="primary"):
                db.update_compte(selected_compte_id, nom_update, statut_update, notes_update, lien_hubspot_update, client_converteo_update)
                st.success("Fiche compte mise à jour !")
                st.rerun()
        with col2_btn:
            if st.form_submit_button("🗑️ Supprimer", use_container_width=True):
                st.session_state.compte_to_delete = selected_compte_id
                st.rerun()

    # --- Logique de confirmation de suppression ---
    if 'compte_to_delete' in st.session_state and st.session_state.compte_to_delete is not None:
        compte_id_del = st.session_state.compte_to_delete
        if compte_id_del in compte_names.values():
            st.warning(f"Êtes-vous sûr de vouloir supprimer définitivement le compte **{selected_compte_name}** et tous les contacts associés ?")
            
            c1_del, c2_del = st.columns(2)
            with c1_del:
                if st.button("✅ Oui, supprimer", use_container_width=True, type="primary"):
                    db.delete_compte(compte_id_del)
                    st.success("Le compte a été supprimé.")
                    del st.session_state.compte_to_delete
                    st.cache_data.clear()
                    st.rerun()
            with c2_del:
                if st.button("❌ Annuler", use_container_width=True):
                    del st.session_state.compte_to_delete
                    st.rerun()

    st.divider()

    # --- Affichage des contacts liés au compte ---
    st.header(f"Contacts ({len(contacts_df)})")
    if not contacts_df.empty:
        st.table(contacts_df[['prenom', 'nom', 'role', 'email']])
    else:
        st.info("Aucun contact n'est associé à ce compte.")

else:
    st.warning("Aucun compte n'a été créé. Utilisez le bouton ci-dessus pour en ajouter un.")