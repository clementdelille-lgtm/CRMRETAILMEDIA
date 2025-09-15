"""
Module for the main dashboard page of the CRM.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import database as db

st.set_page_config(page_title="Accueil CRM", layout="wide")

st.title("🎯 Tableau de Bord de Prospection")
st.info("Utilisez le menu pour naviguer entre la gestion des comptes et des contacts.")

# --- Division en deux colonnes ---
col1, col2 = st.columns(2)

with col1:
    st.header("Actions à traiter")
    today = date.today()
    actions = db.get_actions_a_mener(str(today))

    if actions.empty:
        st.success("🎉 Aucune action en retard ou prévue pour aujourd'hui !")
    else:
        def color_due_date(val):
            """Colors the due date based on its relation to today's date."""
            if pd.isna(val) or val == '':
                return ''

            try:
                due_date = pd.to_datetime(val).date()
                if due_date < today:
                    return 'color: red; font-weight: bold;'
                if due_date == today:
                    return 'color: orange;'
                return ''
            except (ValueError, TypeError):
                return ''

        st.dataframe(
            actions.style.applymap(color_due_date, subset=['date_prochaine_action']),
            use_container_width=True
        )

with col2:
    st.header("Pipeline de Prospection")
    funnel_data = db.get_funnel_data()

    stage_order = ["À qualifier", "Contact établi", "En négociation", "Gagné"]

    if not funnel_data.empty:
        funnel_data = (
            funnel_data.set_index('statut').reindex(stage_order).dropna().reset_index()
        )

    if funnel_data.empty:
        st.warning("Aucune donnée de statut pour afficher le pipeline.")
    else:
        fig = go.Figure(go.Funnel(
            y=funnel_data['statut'],
            x=funnel_data['count'],
            textinfo="value+percent initial",
            marker={"color": ["#004f71", "#008ac5", "#00bfff", "#87ceeb"]}
        ))
        fig.update_layout(margin={"l": 20, "r": 20, "t": 30, "b": 20})
        st.plotly_chart(fig, use_container_width=True)

# --- KPIs en bas de page ---
st.divider()
stats = db.get_stats()
kp1, kp2 = st.columns(2)
kp1.metric("Nombre total de comptes", stats["total_comptes"])
kp2.metric("Nombre total de contacts", stats["total_contacts"])
