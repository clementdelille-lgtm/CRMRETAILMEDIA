# 1_🏠_Accueil.py
import streamlit as st
import database as db
import pandas as pd
from datetime import date
import plotly.graph_objects as go # Importer Plotly

st.set_page_config(page_title="Accueil CRM", layout="wide")

st.title("🎯 Tableau de Bord de Prospection")
st.info("Utilisez le menu sur la gauche pour naviguer entre la gestion des comptes et des contacts.")

# --- Division en deux colonnes ---
col1, col2 = st.columns(2)

with col1:
    # --- FEATURE 1 : ACTIONS À MENER (reste inchangée) ---
    st.header("Actions à traiter")
    today = date.today()
    actions = db.get_actions_a_mener(str(today))

    if actions.empty:
        st.success("🎉 Aucune action en retard ou prévue pour aujourd'hui !")
    else:
        def color_due_date(val):
            due_date = pd.to_datetime(val).date()
            if due_date < today: return 'color: red; font-weight: bold;'
            elif due_date == today: return 'color: orange;'
            else: return ''
        st.dataframe(
            actions.style.applymap(color_due_date, subset=['date_prochaine_action']),
            use_container_width=True
        )

with col2:
    # --- FEATURE 2 : VUE FUNNEL (NOUVEAU) ---
    st.header("Pipeline de Prospection")
    funnel_data = db.get_funnel_data()
    
    # Définir l'ordre des étapes pour un affichage logique
    stage_order = ["À qualifier", "Contact établi", "En négociation", "Gagné"]
    
    # Filtrer et ordonner les données
    funnel_data = funnel_data.set_index('statut').reindex(stage_order).dropna().reset_index()
    
    if funnel_data.empty:
        st.warning("Aucune donnée de statut pour afficher le pipeline.")
    else:
        fig = go.Figure(go.Funnel(
            y = funnel_data['statut'],
            x = funnel_data['count'],
            textinfo = "value+percent initial",
            marker = {"colors": ["#004f71", "#008ac5", "#00bfff", "#87ceeb"]}
            ))
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

# --- KPIs en bas de page ---
st.divider()
stats = db.get_stats()
kp1, kp2 = st.columns(2)
kp1.metric("Nombre total de comptes", stats["total_comptes"])
kp2.metric("Nombre total de contacts", stats["total_contacts"])