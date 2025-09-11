# pages/3_👤_Gestion_Contacts.py
import streamlit as st
import pandas as pd
import database as db
from datetime import date, datetime

st.set_page_config(page_title="Gestion des Contacts", page_icon="👤")
st.title("👤 Fiche de Contact Détaillée")

# --- Sélection du Compte et du Contact ---
all_comptes = db.get_all_comptes()
if all_comptes.empty:
    st.error("Veuillez d'abord ajouter un compte dans la section 'Gestion des Comptes'.")
    st.stop()

# Créer deux colonnes pour une meilleure disposition
col1, col2 = st.columns(2)
with col1:
    compte_names = {row['nom']: row['id'] for index, row in all_comptes.iterrows()}
    selected_compte_name = st.selectbox("Choisissez un compte", options=compte_names.keys())
    selected_compte_id = compte_names[selected_compte_name]

contacts_df = db.get_contacts_for_compte(selected_compte_id)
if contacts_df.empty:
    st.warning("Aucun contact trouvé pour ce compte. Vous pouvez en ajouter un ci-dessous.")
else:
    with col2:
        contact_list = {f"{row['prenom']} {row['nom']}": row['id'] for index, row in contacts_df.iterrows()}
        selected_contact_name = st.selectbox("Sélectionnez un contact", options=contact_list.keys())
        contact_id = contact_list[selected_contact_name]

    st.divider()

    # --- Fiche Contact Complète et Éditable ---
    details = db.get_contact_details(contact_id)
    with st.form(f"fiche_contact_{contact_id}"):
        st.header(f"📝 Fiche de {details.get('prenom')} {details.get('nom')}")

        # Section 1 : Informations Principales
        st.subheader("Informations Principales")
        c1, c2 = st.columns(2)
        with c1:
            prenom = st.text_input("Prénom", value=details.get('prenom', ''))
            email = st.text_input("E-mail", value=details.get('email', ''))
        with c2:
            nom = st.text_input("Nom", value=details.get('nom', ''))
            linkedin = st.text_input("Profil LinkedIn", value=details.get('linkedin', ''))
        
        role = st.text_input("Rôle / Poste", value=details.get('role', ''))
        derniere_action = st.text_area("Notes sur la dernière action", value=details.get('derniere_action', ''))
        
        # Section 2 : Prochaine Action
        st.subheader("⏭️ Prochaine Action")
        c3, c4 = st.columns(2)
        with c3:
            current_date = details.get('date_prochaine_action')
            next_action_date = datetime.strptime(current_date, '%Y-%m-%d').date() if current_date else None
            date_prochaine_action = st.date_input("Date de la prochaine action", value=next_action_date)
        with c4:
            prochaine_action_notes = st.text_input("Description de l'action", value=details.get('prochaine_action_notes', ''))
        
        # Bouton de soumission pour enregistrer toutes les modifications
        if st.form_submit_button("💾 Enregistrer toutes les modifications", use_container_width=True):
            db.update_contact(contact_id, prenom, nom, role, email, linkedin, derniere_action, str(date_prochaine_action) if date_prochaine_action else None, prochaine_action_notes)
            st.success("Fiche contact mise à jour avec succès !")
            st.rerun()

    # --- Section Historique et Ajout d'Interaction ---
    st.header("📖 Historique des Interactions")
    
    # Formulaire pour ajouter une nouvelle interaction
    with st.expander("💬 Ajouter une nouvelle interaction"):
        with st.form("add_interaction_form", clear_on_submit=True):
            interaction_date = st.date_input("Date", value=date.today())
            interaction_type = st.selectbox("Type", ["Email", "Appel", "LinkedIn", "Réunion"])
            interaction_notes = st.text_area("Notes sur l'interaction")
            
            if st.form_submit_button("Ajouter l'interaction"):
                db.add_interaction(contact_id, str(interaction_date), interaction_type, interaction_notes)
                st.success("Interaction ajoutée !")
                st.rerun()

    # Affichage de l'historique
    interactions_df = db.get_interactions_for_contact(contact_id)
    if interactions_df.empty:
        st.info("Aucune interaction enregistrée pour ce contact.")
    else:
        for index, row in interactions_df.iterrows():
            st.markdown(f"**{row['type_interaction']}** - *{row['date_interaction']}*")
            st.markdown(f"> _{row['notes']}_")
            st.markdown("---")


# --- Formulaire d'ajout d'un nouveau contact (en bas de page) ---
st.divider()
with st.expander("➕ Ajouter un nouveau contact à ce compte"):
    with st.form("add_contact_form", clear_on_submit=True):
        st.subheader(f"Nouveau contact pour {selected_compte_name}")
        prenom_new = st.text_input("Prénom")
        nom_new = st.text_input("Nom")
        role_new = st.text_input("Rôle")
        email_new = st.text_input("Email")
        linkedin_new = st.text_input("Profil LinkedIn")
        
        if st.form_submit_button("Créer le contact"):
            # Note : on utilise des valeurs par défaut pour les champs non essentiels à la création
            db.add_contact(prenom_new, nom_new, role_new, email_new, linkedin_new, "", selected_compte_id)
            st.success(f"Contact '{prenom_new} {nom_new}' ajouté à {selected_compte_name} !")
            st.rerun()