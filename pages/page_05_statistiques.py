'''
Module for displaying statistics on prospecting actions.

This page shows two main charts:
1. A pie chart of the distribution of interaction types.
2. A bar chart showing the volume of activity over time (weekly).
'''

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import database as db

def display_interaction_pie_chart():
    """Displays a pie chart of interaction types."""
    st.header("Répartition des Types d'Actions")
    counts_by_type = db.get_interaction_counts_by_type()

    if counts_by_type.empty:
        st.info("Aucune interaction enregistrée pour afficher ce graphique.")
        return

    fig = go.Figure(data=[
        go.Pie(labels=counts_by_type['type_interaction'], values=counts_by_type['count'], hole=.3)
    ])
    fig.update_layout(
        title_text="Proportion des types d'interactions",
        margin={"l": 20, "r": 20, "t": 40, "b": 20}
    )
    st.plotly_chart(fig, use_container_width=True)

def display_activity_over_time_chart():
    """Displays a bar chart of interaction activity over time."""
    st.header("Activité au Fil du Temps")
    interactions_over_time = db.get_interactions_over_time()

    if interactions_over_time.empty:
        st.info("Aucune interaction enregistrée pour afficher ce graphique.")
        return

    # Process data for the chart
    interactions_over_time['date_interaction'] = pd.to_datetime(
        interactions_over_time['date_interaction'], errors='coerce'
    )
    interactions_over_time.dropna(subset=['date_interaction'], inplace=True)

    weekly_activity = (
        interactions_over_time.groupby(pd.Grouper(key='date_interaction', freq='W'))
        .agg(nombre_actions=('date_interaction', 'count'))
        .reset_index()
    )

    # Create and display the chart
    fig = go.Figure(data=[
        go.Bar(x=weekly_activity['date_interaction'], y=weekly_activity['nombre_actions'])
    ])
    fig.update_layout(
        title_text="Nombre d'actions par semaine",
        xaxis_title="Semaine",
        yaxis_title="Nombre d'actions",
        margin={"l": 20, "r": 20, "t": 40, "b": 20}
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main function to run the Streamlit page."""
    st.set_page_config(page_title="Statistiques", page_icon="📈")
    st.title("📈 Statistiques sur les Actions de Prospection")

    display_interaction_pie_chart()
    st.divider()
    display_activity_over_time_chart()

if __name__ == "__main__":
    main()
