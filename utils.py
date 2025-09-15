'''
Utility functions shared across different pages of the application.
'''

import pandas as pd

TAG_STYLE = (
    "background-color: {color}; color: white; padding: 3px 8px; "
    "margin: 2px; border-radius: 5px; display: inline-block;"
)

def render_tags(tags_df: pd.DataFrame) -> str:
    """Renders a DataFrame of tags as an HTML string."""
    if tags_df.empty:
        return ""
    tags_html = "".join(
        f'<span style="{TAG_STYLE.format(color=row["couleur"])}">{row["nom"]}</span>'
        for _, row in tags_df.iterrows()
    )
    return f'<div>{tags_html}</div>'
