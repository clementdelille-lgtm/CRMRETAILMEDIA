# pages/4_🤖_Assistant_IA.py
import streamlit as st
import google.generativeai as genai
import database as db

st.set_page_config(page_title="Assistant IA", page_icon="🤖")
st.title("🤖 Assistant de Prospection IA")

# --- Configuration de l'API Gemini ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erreur de configuration de l'API Gemini. Vérifiez votre fichier secrets.toml : {e}")
    st.stop()

# --- Initialisation de l'historique du chat ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# --- Interface du Chatbot ---
all_contacts = db.get_contacts_with_compte() # Suppose que cette fonction existe
if not all_contacts.empty:
    contact_list = {f"{row['prenom']} {row['nom']} ({row['compte_nom']})": row['id'] for index, row in all_contacts.iterrows()}
    
    selected_contact_name = st.selectbox("Choisissez un contact pour définir le contexte", options=["(Aucun)"] + list(contact_list.keys()))
    
    context_notes = ""
    if selected_contact_name != "(Aucun)":
        contact_id = contact_list[selected_contact_name]
        contact_details = db.get_contact_for_ai(contact_id)
        
        context_notes = f"""
        **Contexte du Contact :**
        - Nom : {contact_details['prenom']} {contact_details['nom']}
        - Rôle : {contact_details['role']}
        - Compte : {contact_details['nom_compte']}
        - Notes de la dernière action ({contact_details['date_derniere_interaction']}): {contact_details['derniere_action']}
        - Notes de la prochaine action ({contact_details['date_prochaine_action']}): {contact_details['prochaine_action_notes']}
        ---
        """
else:
    st.warning("Aucun contact n'a été trouvé. Veuillez en ajouter un pour utiliser l'assistant.")
    st.stop()
    
# Afficher l'historique des messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Boutons de prompts rapides
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Rédiger un email de relance"):
        st.session_state.user_prompt = "Rédige un email de relance court et efficace en te basant sur le contexte."
with col2:
    if st.button("Résumer les notes"):
        st.session_state.user_prompt = "Résume de manière concise toutes les notes de ce contact."
with col3:
    if st.button("Préparer un appel"):
        st.session_state.user_prompt = "Rédige un script de 3 points clés pour un appel de prospection."

# Input de l'utilisateur (pré-rempli par les boutons)
prompt_input = st.chat_input("Votre question...")
if "user_prompt" in st.session_state:
    prompt_input = st.session_state.user_prompt
    del st.session_state.user_prompt

if prompt_input:
    # Ajouter le message de l'utilisateur à l'historique
    st.session_state.chat_history.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    # Préparer le prompt complet pour l'IA
    full_prompt = f"""
    Contexte de prospection :
    ---
    {context_notes}
    ---
    
    Question de l'utilisateur : {prompt_input}
    
    En tant qu'assistant expert en vente et prospection, fournis une réponse utile et concise.
    """
    
    # Obtenir et afficher la réponse de l'IA
    with st.chat_message("assistant"):
        with st.spinner("Réflexion en cours..."):
            response = st.session_state.chat_session.send_message(full_prompt)
            response_text = response.text
            st.markdown(response_text)
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})