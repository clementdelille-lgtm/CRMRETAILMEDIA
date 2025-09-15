'''
Page for managing contacts in the CRM application.

Allows adding, viewing, updating, and deleting contacts,
as well as managing their interactions and tags.
'''
import streamlit as st
import pandas as pd
import database as db
import utils

def get_compte_options():
    """Fetches all accounts and returns them as a dictionary for selectboxes."""
    all_comptes = db.get_all_comptes()
    if all_comptes.empty:
        return {}, all_comptes
    return {row['nom']: row['id'] for _, row in all_comptes.iterrows()}, all_comptes

def display_add_contact_form(tag_names, tag_options):
    """Displays the form to add a new contact."""
    st.header("Ajouter un Contact")

    compte_options, _ = get_compte_options()
    creation_choice = st.radio(
        "Lier à un compte :",
        ('Créer un nouveau compte', 'Choisir un compte existant'),
        horizontal=True,
        key="creation_choice_radio"
    )

    compte_info = {}
    if creation_choice == 'Créer un nouveau compte':
        compte_info['new_name'] = st.text_input(
            "Nom du nouveau compte *", key="new_compte_name_input"
        )
    else:
        if not compte_options:
            st.warning("Aucun compte existant. Veuillez en créer un.")
            st.stop()
        compte_info['selected_name'] = st.selectbox(
            "Choisir un compte existant",
            options=list(compte_options.keys()),
            key="existing_compte_select"
        )
        compte_info['selected_id'] = compte_options.get(compte_info['selected_name'])

    with st.form("add_contact_form", clear_on_submit=True):
        contact_info = gather_contact_info(tag_names)
        if st.form_submit_button("Créer le contact", use_container_width=True):
            handle_add_contact_submission(
                creation_choice, compte_info, contact_info, tag_options
            )

def gather_contact_info(tag_names):
    """Gathers contact information from the user."""
    st.subheader("Informations du contact")
    return {
        "prenom": st.text_input("Prénom *"),
        "nom": st.text_input("Nom *"),
        "role": st.text_input("Rôle"),
        "email": st.text_input("Email"),
        "linkedin": st.text_input("Profil LinkedIn"),
        "statut_prospection": st.selectbox(
            "Statut de Prospection",
            options=["À Contacter", "Contacté", "Intéressé", "Non intéressé"]
        ),
        "tags_selection": st.multiselect("Associer des tags", options=tag_names)
    }

def handle_add_contact_submission(
    creation_choice, compte_info, contact_info, tag_options
):
    """Handles the logic after submitting the 'add contact' form."""
    final_compte_id, compte_name = get_final_compte_info(creation_choice, compte_info)

    if not contact_info["prenom"] or not contact_info["nom"]:
        st.error("Le prénom et le nom du contact sont obligatoires.")
        return

    if final_compte_id:
        contact_info['compte_id'] = final_compte_id
        tags = contact_info.pop('tags_selection')
        new_contact_id = db.add_contact(**contact_info)
        if new_contact_id:
            selected_tag_ids = [tag_options[name] for name in tags]
            db.update_tags_for_entity(new_contact_id, selected_tag_ids, "contact")
            st.success(
                f"Contact '{contact_info['prenom']} {contact_info['nom']}' "
                f"ajouté à {compte_name} !"
            )
            st.session_state.show_add_contact_form = False
            st.rerun()

def get_final_compte_info(creation_choice, compte_info):
    """Determines the final account ID and name based on user's choice."""
    if creation_choice == 'Créer un nouveau compte':
        if not compte_info['new_name']:
            st.error("Le nom du nouveau compte est obligatoire.")
            st.stop()
        return db.add_compte(
            nom=compte_info['new_name'], statut="À qualifier", client_converteo="Non"
        ), compte_info['new_name']
    return compte_info['selected_id'], compte_info['selected_name']

def display_view_modify_contact(tag_names, tag_options):
    """Displays the section to view and modify an existing contact."""
    st.header("Consulter et Modifier une Fiche Contact")
    compte_options, _ = get_compte_options()
    if not compte_options:
        st.warning("Créez d'abord un compte dans la page 'Gestion des Comptes'.")
        return

    selected_compte_name = st.selectbox(
        "Choisissez un compte pour voir ses contacts",
        options=list(compte_options.keys()), key="view_compte"
    )
    selected_compte_id = compte_options[selected_compte_name]
    
    contacts_df = db.get_contacts_for_compte(selected_compte_id)
    if contacts_df.empty:
        st.info("Aucun contact à afficher pour ce compte.")
        return

    contact_list = {
        f"{row['prenom']} {row['nom']}": row['id'] for _, row in contacts_df.iterrows()
    }
    selected_contact_name = st.selectbox(
        "Sélectionnez un contact", options=list(contact_list.keys()), key="view_contact"
    )
    contact_id = contact_list[selected_contact_name]
    display_contact_details(contact_id, tag_names, tag_options)

def display_contact_details(contact_id, tag_names, tag_options):
    """Displays the detailed form for a specific contact."""
    details = db.get_contact_details(contact_id)
    contact_tags_df = db.get_tags_for_entity(contact_id, "contact")
    st.subheader(f"📝 Fiche de {details.get('prenom')} {details.get('nom')}")
    st.markdown(utils.render_tags(contact_tags_df), unsafe_allow_html=True)
    st.write("---")

    with st.form(f"fiche_contact_{contact_id}"):
        updated_info = gather_updated_contact_info(details, contact_tags_df, tag_names)
        submit_col, delete_col = st.columns([3, 1])
        if submit_col.form_submit_button(
            "💾 Enregistrer les modifications", use_container_width=True, type="primary"
        ):
            handle_update_contact(contact_id, updated_info, tag_options)
        if delete_col.form_submit_button("🗑️ Supprimer", use_container_width=True):
            st.session_state.contact_to_delete = contact_id
            st.rerun()

    handle_delete_confirmation(contact_id, details)
    st.divider()
    st.header("📖 Historique des Interactions")

def gather_updated_contact_info(details, contact_tags_df, tag_names):
    """Gathers updated contact information from the user."""
    st.markdown("##### Informations Principales")
    c1, c2 = st.columns(2)
    with c1:
        prenom = st.text_input("Prénom", value=details.get('prenom', ''))
        email = st.text_input("E-mail", value=details.get('email', ''))
    with c2:
        nom = st.text_input("Nom", value=details.get('nom', ''))
        linkedin = st.text_input("Profil LinkedIn", value=details.get('linkedin', ''))
    role = st.text_input("Rôle / Poste", value=details.get('role', ''))
    status_options = ["À Contacter", "Contacté", "Intéressé", "Non intéressé"]
    current_status = details.get('statut_prospection')
    status_index = status_options.index(current_status) if current_status in status_options else 0
    statut_prospection = st.selectbox(
        "Statut de Prospection", options=status_options, index=status_index
    )
    st.text_area(
        "Notes sur la dernière action", value=details.get('derniere_action', '')
    )
    st.markdown("##### 🏷️ Tags")
    default_tags = list(contact_tags_df['nom'])
    tags_selection = st.multiselect(
        "Modifier les tags associés", options=tag_names, default=default_tags
    )
    return {"prenom": prenom, "nom": nom, "role": role, "email": email, 
            "linkedin": linkedin, "statut_prospection": statut_prospection, 
            "tags": tags_selection}

def handle_update_contact(contact_id, updated_info, tag_options):
    """Handles the logic for updating a contact's details."""
    tags = updated_info.pop('tags')
    db.update_contact(contact_id, **updated_info)
    selected_tag_ids = [tag_options.get(name) for name in tags]
    db.update_tags_for_entity(
        contact_id, [tag_id for tag_id in selected_tag_ids if tag_id], "contact"
    )
    st.success("Fiche contact mise à jour !")
    st.rerun()

def handle_delete_confirmation(contact_id, details):
    """Handles the confirmation logic for deleting a contact."""
    if st.session_state.get('contact_to_delete') == contact_id:
        st.warning(
            f"Êtes-vous sûr de vouloir supprimer **{details.get('prenom')} "
            f"{details.get('nom')}** ?"
        )
        confirm_col, cancel_col = st.columns(2)
        if confirm_col.button(
            "✅ Oui, supprimer", use_container_width=True, type="primary"
        ):
            db.delete_contact(contact_id)
            st.session_state.contact_to_delete = None
            st.rerun()
        if cancel_col.button("❌ Annuler", use_container_width=True):
            st.session_state.contact_to_delete = None
            st.rerun()

def main():
    """Main function to run the Streamlit page."""
    st.set_page_config(page_title="Gestion des Contacts", page_icon="👤")
    st.title("👤 Gestion des Contacts")
    try:
        all_tags = db.get_all_tags()
        tag_options = {row['nom']: row['id'] for _, row in all_tags.iterrows()}
        tag_names = list(tag_options.keys())
    except Exception as e:
        st.error(f"Erreur lors du chargement des tags : {e}")
        tag_options, tag_names = {}, []

    st.session_state.setdefault('show_add_contact_form', False)

    if st.button("➕ Nouveau Contact", type="primary"):
        st.session_state.show_add_contact_form = not st.session_state.show_add_contact_form
        st.session_state.pop('contact_to_delete', None)

    if st.session_state.show_add_contact_form:
        display_add_contact_form(tag_names, tag_options)

    st.divider()
    display_view_modify_contact(tag_names, tag_options)

if __name__ == "__main__":
    main()
