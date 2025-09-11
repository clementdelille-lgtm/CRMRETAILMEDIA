# pages/4_🤖_Assistant_IA.py
import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Assistant IA", page_icon="🤖")
st.title("🤖 Assistant de Prospection IA")

# --- Configuration de l'API Gemini ---
try:
    # Récupérer la clé API depuis les secrets Streamlit
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erreur de configuration de l'API Gemini. Vérifiez votre fichier secrets.toml : {e}")
    st.stop()

# --- Initialisation de l'historique du chat ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Interface du Chatbot ---
st.info("Copiez-collez les notes sur votre prospect ou votre compte ci-dessous, puis posez votre question.")

context = st.text_area("Contexte (notes sur le contact, historique, etc.)", height=150, key="context_area")

# Afficher l'historique des messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input de l'utilisateur
if prompt := st.chat_input("Votre question (ex: 'Rédige un email de relance court')"):
    # Ajouter le message de l'utilisateur à l'historique
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Préparer le prompt complet pour l'IA
    full_prompt = f"""
    Contexte de prospection :
    ---
    {context}
    ---
    
    Question de l'utilisateur : {prompt}
    
    En tant qu'assistant expert en vente et prospection, fournis une réponse utile et concise.
    """
    
    # Obtenir et afficher la réponse de l'IA
    with st.chat_message("assistant"):
        with st.spinner("Réflexion en cours..."):
            response = model.generate_content(full_prompt)
            response_text = response.text
            st.markdown(response_text)
            # Ajouter la réponse de l'IA à l'historique
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})