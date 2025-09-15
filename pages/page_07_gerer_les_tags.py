'''
This module allows users to manage tags in the CRM, including creating,
updating, and deleting them.
'''

import streamlit as st
import pandas as pd
import database as db

def display_create_tag_form():
    """Displays the form to create a new tag."""
    st.header("➕ Créer un nouveau Tag")
    with st.form("new_tag_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nom du tag", placeholder="Ex: Décideur, Tech")
        with col2:
            color = st.color_picker("Couleur du tag", "#4e8ec6")
        
        if st.form_submit_button("Ajouter le Tag", use_container_width=True, type="primary"):
            if name:
                if db.add_tag(name, color):
                    st.success(f"Tag '{name}' créé avec succès !")
                    st.rerun()
            else:
                st.warning("Le nom du tag ne peut pas être vide.")

def handle_tag_updates(original_df, edited_df):
    """Handles the logic for updating, adding, or deleting tags."""
    original_records = original_df.to_dict("records")
    edited_records = edited_df.to_dict("records")
    original_ids = {rec['id'] for rec in original_records}
    edited_ids = {rec.get('id') for rec in edited_records}

    # Handle deletions
    deleted_ids = original_ids - edited_ids
    for tag_id in deleted_ids:
        db.delete_tag(tag_id)
        st.toast(f"Tag ID {tag_id} supprimé.")

    # Handle additions and modifications
    for record in edited_records:
        tag_id = record.get('id')
        if pd.isna(tag_id) or tag_id not in original_ids:
            if record.get("nom"):
                db.add_tag(record["nom"], record["couleur"])
                st.toast(f"Tag '{record['nom']}' ajouté.")
        else:
            original_record = next(item for item in original_records if item["id"] == tag_id)
            if original_record['nom'] != record['nom'] or original_record['couleur'] != record['couleur']:
                db.update_tag(tag_id, record["nom"], record["couleur"])
                st.toast(f"Tag '{record['nom']}' mis à jour.")

    st.rerun()

def display_manage_tags():
    """Displays the interactive editor for existing tags."""
    st.header("🗂️ Tags Existants")
    try:
        all_tags = db.get_all_tags()
        if all_tags.empty:
            st.info("Aucun tag créé. Utilisez le formulaire ci-dessus pour en ajouter.")
            return

        # Use a data editor for an interactive grid
        edited_df = st.data_editor(
            all_tags,
            column_config={
                "id": None,  # Hide the ID column
                "nom": st.column_config.TextColumn("Nom du Tag", required=True),
                "couleur": st.column_config.ColorColumn("Couleur"),
            },
            use_container_width=True,
            num_rows="dynamic",
            key="tags_editor"
        )

        if st.button("Enregistrer les modifications", type="primary"):
            handle_tag_updates(all_tags, pd.DataFrame(edited_df))

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
        st.warning("Vérifiez la connexion à la base de données.")

def main():
    """Main function to orchestrate the page.
    Note: Renamed the file to remove non-ASCII characters and use snake_case.
    """
    st.set_page_config(page_title="Gérer les Tags", page_icon="🏷️")
    st.title("🏷️ Gérer les Tags")

    display_create_tag_form()
    st.divider()
    display_manage_tags()

if __name__ == "__main__":
    main()
