# pages/5_📈_Statistiques.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import database as db

st.set_page_config(page_title="Statistiques", page_icon="📈")
st.title("📈 Statistiques sur les Actions de Prospection")

# --- Graphique 1 : Répartition des types d'interactions ---
st.header("Répartition des Types d'Actions")
counts_by_type = db.get_interaction_counts_by_type()

if not counts_by_type.empty:
    fig_pie = go.Figure(data=[go.Pie(
        labels=counts_by_type['type_interaction'],
        values=counts_by_type['count'],
        hole=.3 # Pour un effet donut
    )])
    fig_pie.update_layout(
        title_text="Proportion des types d'interactions",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("Aucune interaction enregistrée pour afficher ce graphique.")

st.divider()

# --- Graphique 2 : Volume d'activité dans le temps ---
st.header("Activité au Fil du Temps")
interactions_over_time = db.get_interactions_over_time()

if not interactions_over_time.empty:
    # Convertir la colonne de date en format datetime
    interactions_over_time['date_interaction'] = pd.to_datetime(interactions_over_time['date_interaction'])
    
    # Agréger le nombre d'interactions par semaine
    weekly_activity = interactions_over_time.resample('W-Mon', on='date_interaction').count()
    weekly_activity.rename(columns={'date_interaction': 'nombre_actions'}, inplace=True)
    
    fig_bar = go.Figure(data=[go.Bar(
        x=weekly_activity.index,
        y=weekly_activity['nombre_actions'],
    )])
    fig_bar.update_layout(
        title_text="Nombre d'actions par semaine",
        xaxis_title="Semaine",
        yaxis_title="Nombre d'actions",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Aucune interaction enregistrée pour afficher ce graphique.")