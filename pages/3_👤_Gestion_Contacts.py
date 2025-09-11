# pages/3_👤_Gestion_Contacts.py
import streamlit as st
import pandas as pd
import database as db
from datetime import date, datetime

st.set_page_config(page_title="Gestion des Contacts", page_icon="👤")
st.title("👤 Gestion des Contacts")

# --- Logique pour afficher/masquer le formulaire d'ajout ---
if 'show_add_contact_form' not in st.session_state:
    st.session_state.show_add_contact_form = False

if st.button("➕ Nouveau Contact", type="primary"):
    st.session_state.show_add_contact_form = not st.session_state.show_add_contact_form

# --- Le formulaire d'ajout ne s'affiche que si notre variable est True ---
if st.session_state.show_add_contact_form:
    with st.form("add_contact_form", clear_on_submit=True):
        st.header("Ajouter un Contact")
        
        all_comptes = db.get_all_comptes()
        compte_names = {row['nom']: row['id'] for index, row in all_comptes.iterrows()}

        create_new_compte = st.checkbox("Créer un nouveau compte en même temps")
        
        if create_new_compte:
            new_compte_name = st.text_input("Nom du nouveau compte *")
        else:
            if not all_comptes.empty:
                selected_compte_name = st.selectbox("Choisir un compte existant", options=compte_names.keys())
            else:
                st.warning("Aucun compte existant. Cochez la case ci-dessus pour en créer un.")
                selected_compte_name = None

        st.subheader("Informations du nouveau contact")
        prenom_new = st.text_input("Prénom *")
        nom_new = st.text_input("Nom *")
        role_new = st.text_input("Rôle")
        email_new = st.text_input("Email")
        linkedin_new = st.text_input("Profil LinkedIn")
        
        # Le bouton de soumission pour le formulaire d'ajout
        if st.form_submit_button("Créer le contact", use_container_width=True):
            if create_new_compte:
                if not new_compte_name or not prenom_new or not nom_new:
                    st.error("Le nom du nouveau compte, le prénom et le nom du contact sont obligatoires.")
                else:
                    db.add_compte(new_compte_name, "À qualifier", "", "", "N")
                    new_compte_id = db.get_all_comptes().set_index('nom').loc[new_compte_name]['id']
                    db.add_contact(prenom_new, nom_new, role_new, email_new, linkedin_new, "", new_compte_id)
                    st.success(f"Compte '{new_compte_name}' et contact '{prenom_new} {nom_new}' créés !")
                    st.session_state.show_add_contact_form = False
                    st.rerun()
            else:
                if not prenom_new or not nom_new:
                    st.error("Le prénom et le nom du contact sont obligatoires.")
                elif selected_compte_name is None:
                    st.error("Veuillez sélectionner un compte ou en créer un nouveau.")
                else:
                    selected_compte_id = compte_names[selected_compte_name]
                    db.add_contact(prenom_new, nom_new, role_new, email_new, linkedin_new, "", selected_compte_id)
                    st.success(f"Contact '{prenom_new} {nom_new}' ajouté à {selected_compte_name} !")
                    st.session_state.show_add_contact_form = False
                    st.rerun()

st.divider()

# --- Section de consultation et modification ---
st.header("Consulter et Modifier une Fiche Contact")
all_comptes_for_view = db.get_all_comptes()

if not all_comptes_for_view.empty:
    compte_names_for_view = {row['nom']: row['id'] for index, row in all_comptes_for_view.iterrows()}
    selected_compte_name_for_view = st.selectbox("Choisissez un compte pour voir ses contacts", options=compte_names_for_view.keys(), key="view_compte")
    selected_compte_id_for_view = compte_names_for_view[selected_compte_name_for_view]
    
    contacts_df = db.get_contacts_for_compte(selected_compte_id_for_view)
    if contacts_df.empty:
        st.info("Aucun contact à afficher pour ce compte.")
    else:
        contact_list = {f"{row['prenom']} {row['nom']}": row['id'] for index, row in contacts_df.iterrows()}
        selected_contact_name = st.selectbox("Sélectionnez un contact", options=contact_list.keys(), key="view_contact")
        contact_id = contact_list[selected_contact_name]
        details = db.get_contact_details(contact_id)

        # Formulaire de la fiche de contact
        with st.form(f"fiche_contact_{contact_id}"):
            st.subheader(f"📝 Fiche de {details.get('prenom')} {details.get('nom')}")

            st.markdown("##### Informations Principales")
            c1, c2 = st.columns(2)
            with c1:
                prenom = st.text_input("Prénom", value=details.get('prenom', ''))
                email = st.text_input("E-mail", value=details.get('email', ''))
            with c2:
                nom = st.text_input("Nom", value=details.get('nom', ''))
                linkedin = st.text_input("Profil LinkedIn", value=details.get('linkedin', ''))
            
            role = st.text_input("Rôle / Poste", value=details.get('role', ''))
            derniere_action = st.text_area("Notes sur la dernière action", value=details.get('derniere_action', ''))
            
            st.markdown("##### ⏭️ Prochaine Action")
            c3, c4 = st.columns(2)
            with c3:
                current_date_str = details.get('date_prochaine_action')
                next_action_date = datetime.strptime(current_date_str, '%Y-%m-%d').date() if current_date_str else None
                date_prochaine_action = st.date_input("Date de la prochaine action", value=next_action_date)
            with c4:
                prochaine_action_notes = st.text_input("Description de l'action", value=details.get('prochaine_action_notes', ''))
            
            # Le bouton de soumission pour la fiche de contact
            if st.form_submit_button("💾 Enregistrer toutes les modifications", use_container_width=True):
                date_to_save = str(date_prochaine_action) if date_prochaine_action else None
                db.update_contact(contact_id, prenom, nom, role, email, linkedin, derniere_action, date_to_save, prochaine_action_notes)
                st.success("Fiche contact mise à jour avec succès !")
                st.rerun()

        # Section Historique et Ajout d'Interaction
        st.header("📖 Historique des Interactions")
        with st.expander("💬 Ajouter une nouvelle interaction"):
            with st.form("add_interaction_form", clear_on_submit=True):
                interaction_date = st.date_input("Date", value=date.today())
                interaction_type = st.selectbox("Type", ["Email", "Appel", "LinkedIn", "Réunion"])
                interaction_notes = st.text_area("Notes sur l'interaction")
                
                # Le bouton de soumission pour l'ajout d'interaction
                if st.form_submit_button("Ajouter l'interaction"):
                    db.add_interaction(contact_id, str(interaction_date), interaction_type, interaction_notes)
                    st.success("Interaction ajoutée !")
                    st.rerun()

        interactions_df = db.get_interactions_for_contact(contact_id)
        if interactions_df.empty:
            st.info("Aucune interaction enregistrée pour ce contact.")
        else:
            for index, row in interactions_df.iterrows():
                st.markdown(f"**{row['type_interaction']}** - *{row['date_interaction']}*")
                st.markdown(f"> _{row['notes']}_")
                st.markdown("---")
else:
    st.warning("Aucun compte n'a été créé. Ajoutez-en un d'abord via la page 'Gestion des Comptes'.")