import plotly.graph_objects as go
import plotly.express as px
import hover_template as hover

from preprocess import AGE_MIDPOINTS
from theme import GOLD, SILVER, BRONZE

medal_colors = {"Gold": GOLD, "Silver": SILVER, "Bronze": BRONZE}

def create_medal_age_bubble(grouped):
    '''
    Creates a bubble plot of age distribution for medals (Visualization 3).
    '''
    fig = px.scatter(grouped,
                     x="Medal",
                     y="Age_Midpoint",
                     size="Count",
                     color="Medal",
                     labels={"Medal": "Medal Type", "Age_Midpoint": "Age Group", "Count": "Number of Medalists"},
                     opacity=0.85,
                     color_discrete_map=medal_colors,
                     size_max=40)

    fig.update_yaxes(tickvals=list(AGE_MIDPOINTS.values()), ticktext=list(AGE_MIDPOINTS.keys()),
                     title="Age Group")
    
    fig.update_xaxes(categoryorder="array", categoryarray=["Gold", "Silver", "Bronze"]) 
    
    fig.update_traces(hovertemplate=hover.medal_distribution_hover()) 
    
    return fig