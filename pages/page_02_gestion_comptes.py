'''
Page for managing accounts in the CRM application.

Allows adding, viewing, updating, and deleting accounts, as well as managing their tags.
'''
import streamlit as st
import pandas as pd
import database as db
import utils

def get_tag_data():
    """Fetches all tags and prepares them for dropdowns."""
    try:
        all_tags = db.get_all_tags()
        tag_options = {row['nom']: row['id'] for _, row in all_tags.iterrows()}
        tag_names = list(tag_options.keys())
        return tag_names, tag_options
    except Exception as e:
        st.error(f"Erreur lors du chargement des tags : {e}")
        return [], {}

def display_add_compte_form(tag_names, tag_options):
    """Displays the form to add a new account."""
    with st.form("add_compte_form", clear_on_submit=True):
        st.header("Ajouter un Compte")
        nom = st.text_input("Nom de l'entreprise *")

        c1, c2 = st.columns(2)
        with c1:
            statut = st.selectbox(
                "Statut",
                options=["À qualifier", "En cours", "Opportunité", "Client", "Fermé/Perdu"]
            )
        with c2:
            client_converteo = st.selectbox("Client Converteo ?", options=["Oui", "Non"])

        lien_hubspot = st.text_input("Lien Hubspot")
        notes = st.text_area("Notes sur le compte")
        tags_selection = st.multiselect("Associer des tags", options=tag_names)

        if st.form_submit_button("Créer le compte", use_container_width=True):
            handle_add_compte_submission(
                nom, statut, notes, lien_hubspot, client_converteo, 
                tags_selection, tag_options
            )

def handle_add_compte_submission(
    nom, statut, notes, lien_hubspot, client_converteo, 
    tags_selection, tag_options
):
    """Handles the logic after submitting the 'add account' form."""
    if not nom:
        st.error("Le nom de l'entreprise est obligatoire.")
        return

    new_compte_id = db.add_compte(
        nom=nom, statut=statut, notes=notes, 
        lien_hubspot=lien_hubspot, client_converteo=client_converteo
    )
    if new_compte_id:
        selected_tag_ids = [tag_options.get(name) for name in tags_selection]
        db.update_tags_for_entity(
            new_compte_id, 
            [tag_id for tag_id in selected_tag_ids if tag_id], 
            "compte"
        )
        st.success(f"Le compte '{nom}' a été créé !")
        st.session_state.show_add_compte_form = False
        st.rerun()

def display_view_modify_compte(tag_names, tag_options):
    """Displays the section to view and modify an existing account."""
    st.header("Consulter et Modifier un Compte")
    all_comptes = db.get_all_comptes()

    if all_comptes.empty:
        st.warning(
            "Aucun compte n'a été créé. "
            "Utilisez le bouton ci-dessus pour en ajouter un."
        )
        return

    compte_names_dict = {row['nom']: row['id'] for _, row in all_comptes.iterrows()}
    selected_compte_name = st.selectbox(
        "Choisissez un compte", options=list(compte_names_dict.keys()), key="view_compte"
    )
    selected_compte_id = compte_names_dict[selected_compte_name]

    display_compte_details(
        selected_compte_id, selected_compte_name, tag_names, tag_options
    )

def display_compte_details(compte_id, compte_name, tag_names, tag_options):
    """Displays the detailed form for a specific account."""
    details = db.get_compte_details(compte_id)
    contacts_df = db.get_contacts_for_compte(compte_id)
    compte_tags_df = db.get_tags_for_entity(compte_id, "compte")

    st.subheader(f"📝 Fiche de {details.get('nom')}")
    st.markdown(utils.render_tags(compte_tags_df), unsafe_allow_html=True)
    st.write("---")

    with st.form("fiche_compte_form"):
        c1, c2 = st.columns(2)
        with c1:
            nom_update = st.text_input(
                "Nom de l'entreprise", value=details.get('nom')
            )
            status_options = [
                "À qualifier", "En cours", "Opportunité", "Client", "Fermé/Perdu"
            ]
            current_status = details.get('statut')
            status_index = status_options.index(current_status) if current_status in status_options else 0
            statut_update = st.selectbox(
                "Statut", options=status_options, index=status_index
            )
        with c2:
            lien_hubspot_update = st.text_input(
                "Lien Hubspot", value=details.get('lien_hubspot', '')
            )
            client_opts = ["Oui", "Non"]
            client_idx = client_opts.index(details.get('client_converteo', 'Non'))
            client_converteo_update = st.selectbox(
                "Client Converteo ?", options=client_opts, index=client_idx
            )

        notes_update = st.text_area("Notes", value=details.get('notes', ''))

        st.subheader("🏷️ Tags")
        default_tags = list(compte_tags_df['nom'])
        tags_update_selection = st.multiselect(
            "Modifier les tags associés", options=tag_names, default=default_tags
        )

        submit_col, delete_col = st.columns([3, 1])
        if submit_col.form_submit_button(
            "💾 Enregistrer", use_container_width=True, type="primary"
        ):
            handle_update_compte(
                compte_id, nom_update, statut_update, notes_update,
                lien_hubspot_update, client_converteo_update,
                tags_update_selection, tag_options
            )
        if delete_col.form_submit_button("🗑️ Supprimer", use_container_width=True):
            st.session_state.compte_to_delete = compte_id
            st.rerun()

    handle_delete_confirmation(compte_id, compte_name)

    st.divider()
    st.header(f"Contacts ({len(contacts_df)})")
    if not contacts_df.empty:
        st.table(contacts_df[['prenom', 'nom', 'role', 'email']])
    else:
        st.info("Aucun contact n'est associé à ce compte.")

def handle_update_compte(
    compte_id, nom, statut, notes, lien_hubspot, client_converteo, tags, tag_options
):
    """Handles the logic for updating an account's details."""
    db.update_compte(
        compte_id, nom=nom, statut=statut, notes=notes, 
        lien_hubspot=lien_hubspot, client_converteo=client_converteo
    )
    selected_tag_ids = [tag_options.get(name) for name in tags]
    db.update_tags_for_entity(
        compte_id, [tag_id for tag_id in selected_tag_ids if tag_id], "compte"
    )
    st.success("Fiche compte mise à jour !")
    st.rerun()

def handle_delete_confirmation(compte_id, compte_name):
    """Handles the confirmation logic for deleting an account."""
    if st.session_state.get('compte_to_delete') == compte_id:
        st.warning(
            f"Supprimer **{compte_name}** supprimera aussi tous les contacts associés. "
            f"Êtes-vous sûr ?"
        )
        confirm_col, cancel_col = st.columns(2)
        if confirm_col.button(
            "✅ Oui, supprimer", use_container_width=True, type="primary"
        ):
            db.delete_compte(compte_id)
            st.success("Le compte a été supprimé.")
            st.session_state.compte_to_delete = None
            st.rerun()
        if cancel_col.button("❌ Annuler", use_container_width=True):
            st.session_state.compte_to_delete = None
            st.rerun()

def main():
    """Main function to run the Streamlit page."""
    st.set_page_config(page_title="Gestion des Comptes", page_icon="🏢")
    st.title("🏢 Gestion des Comptes")

    tag_names, tag_options = get_tag_data()

    st.session_state.setdefault('show_add_compte_form', False)

    if st.button("➕ Nouveau Compte", type="primary"):
        st.session_state.show_add_compte_form = \
            not st.session_state.show_add_compte_form
        st.session_state.compte_to_delete = None

    if st.session_state.show_add_compte_form:
        display_add_compte_form(tag_names, tag_options)

    st.divider()
    display_view_modify_compte(tag_names, tag_options)

if __name__ == "__main__":
    main()
