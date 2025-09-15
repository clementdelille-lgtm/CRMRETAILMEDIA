"""
Module for the AI prospecting assistant page.
"""
import streamlit as st
import google.generativeai as genai
import database as db

st.set_page_config(page_title="Assistant IA", page_icon="🤖")
st.title("🤖 Assistant de Prospection IA")

# --- Configuration of the Gemini API ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(
        f"Erreur de configuration de l'API Gemini. "
        f"Vérifiez votre fichier secrets.toml : {e}"
    )
    st.stop()

# --- Initialization of chat history ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# --- Chatbot Interface ---
all_contacts = db.get_contacts_with_compte()
context_notes = ""

if all_contacts.empty:
    st.warning("Aucun contact trouvé. Ajoutez-en un pour utiliser l'assistant.")
    st.stop()

contact_list = {
    f"{row['prenom']} {row['nom']} ({row['compte_nom']})": row['id']
    for _, row in all_contacts.iterrows()
}

options = ["(Aucun)"] + list(contact_list.keys())
selected_contact_name = st.selectbox(
    "Choisissez un contact pour définir le contexte", options=options
)

if selected_contact_name != "(Aucun)":
    contact_id = contact_list[selected_contact_name]
    contact_details = db.get_contact_for_ai(contact_id)

    context_notes = f"""
    **Contexte du Contact :**
    - Nom : {contact_details['prenom']} {contact_details['nom']}
    - Rôle : {contact_details['role']}
    - Compte : {contact_details['nom_compte']}
    - Dernière action ({contact_details['date_derniere_interaction']}): 
      {contact_details['derniere_action']}
    - Prochaine action ({contact_details['date_prochaine_action']}): 
      {contact_details['prochaine_action_notes']}
    ---
    """

# Display message history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def handle_quick_prompt(prompt):
    """Handles the logic for quick prompt buttons."""
    st.session_state.user_prompt = prompt

# Quick prompt buttons
col1, col2, col3 = st.columns(3)
if col1.button("Rédiger un email de relance"):
    handle_quick_prompt("Rédige un email de relance court et efficace.")
if col2.button("Résumer les notes"):
    handle_quick_prompt("Résume de manière concise toutes les notes de ce contact.")
if col3.button("Préparer un appel"):
    handle_quick_prompt("Rédige un script de 3 points clés pour un appel.")

# User input
prompt_input = st.chat_input("Votre question...")
if "user_prompt" in st.session_state:
    prompt_input = st.session_state.user_prompt
    del st.session_state.user_prompt

if prompt_input:
    st.session_state.chat_history.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    full_prompt = f"""
    Contexte de prospection :
    ---
    {context_notes}
    ---
    Question : {prompt_input}
    En tant qu'assistant expert en vente, fournis une réponse utile et concise.
    """

    with st.chat_message("assistant"), st.spinner("Réflexion en cours..."):
        response = st.session_state.chat_session.send_message(full_prompt)
        response_text = response.text
        st.markdown(response_text)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response_text}
        )
